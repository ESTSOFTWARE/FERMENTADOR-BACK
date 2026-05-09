# Refactoring — Desacoplamiento SOA y corrección de arquitectura

**Rama:** `refactor/amethdev-architecture-structure`  
**Fecha:** 2026-05-09

---

## Contexto

El proyecto seguía una estructura SOA en carpetas pero los servicios se comunicaban directamente entre sí importando código de otros servicios. Este refactoring elimina esos acoplamientos y corrige bugs de imports rotos que quedaron del refactoring anterior.

---

## 1. Corrección de imports rotos

Durante el refactoring anterior, el archivo `entities.py` de cada servicio fue dividido en archivos separados (`sensor_reading.py`, `fermentation_session.py`, etc.), pero varios archivos no fueron actualizados y seguían importando desde la ruta antigua que ya no existía.

**Archivos corregidos:**

| Archivo | Antes | Después |
|---|---|---|
| `sensors/domain/repository.py` | `.entities.entities` | `.entities.sensor_reading` |
| `sensors/usecase/get_history_use_case.py` | `.entities.entities` | `.entities.sensor_reading` |
| `sensors/usecase/save_reading_use_case.py` | `.entities.entities` | `.entities.sensor_reading` |
| `fermentation/domain/repository.py` | `.entities.entities` | imports individuales por entidad |
| `fermentation/usecase/get_report_use_case.py` | `.entities.entities` | `.entities.fermentation_report` |
| `fermentation/usecase/get_sessions_history_use_case.py` | `.entities.entities` | `.entities.fermentation_session` |
| `fermentation/usecase/schedule_fermentation_use_case.py` | `.entities.entities` | `.entities.fermentation_session` |
| `fermentation/usecase/start_fermentation_use_case.py` | `.entities.entities` | `.entities.fermentation_session` |
| `fermentation/usecase/get_report_history_use_case.py` | `.entities.entities` | `.entities.report_history` |
| `fermentation/usecase/stop_fermentation_use_case.py` | `.entities.entities` | `.entities.fermentation_session` |

**Bug adicional corregido:** `SensorDeactivatedMessage` en `save_reading_use_case.py` usaba el campo `deactivated_at` que no existía en el schema. Corregido a `occurred_at` y se agregó `last_reading` que faltaba.

---

## 2. Desacoplamiento de servicios

Se identificaron y resolvieron 6 acoplamientos entre servicios. En cada caso, un servicio importaba directamente código de infraestructura de otro servicio.

---

### 2.1 sensors → fermentation

**Problema:** `save_reading_use_case.execute_deactivation()` importaba `FermentationRepository` directamente e instanciaba `AsyncSessionLocal` para llamar a `update_sensor_deactivation()`. El servicio de sensores sabía de la existencia y la implementación del servicio de fermentación.

**Solución:** Comunicación por evento RabbitMQ.

**Flujo anterior:**
```
sensor desactivado
  → sensors llama directamente a FermentationRepository.update_sensor_deactivation()
```

**Flujo nuevo:**
```
sensor desactivado
  → sensors publica evento en RabbitMQ (exchange: sensor.events, routing key: sensor.deactivated)
  → FermentationEventConsumer escucha sensor.deactivated.queue
  → llama a FermentationRepository.update_sensor_deactivation()
```

**Payload del evento `sensor.deactivated`:**
```json
{
  "session_id": 7,
  "sensor_type": "alcohol",
  "last_reading": 65.2,
  "deactivated_at": "2026-05-09T10:30:00+00:00"
}
```

**Archivos nuevos:**
- `src/core/rabbitmq/exchanges.py` — se agrega exchange `sensor.events` (TOPIC, durable) y queue `sensor.deactivated.queue` (TTL 5min, max 5000 mensajes)
- `src/services/fermentation/infrastructure/event_consumer.py` — `FermentationEventConsumer` que escucha y procesa el evento

**Archivos modificados:**
- `src/services/sensors/application/usecase/save_reading_use_case.py` — `execute_deactivation()` ahora publica el evento en vez de llamar directamente
- `main.py` — wiring del `FermentationEventConsumer` en startup y shutdown

---

### 2.2 fermentation → sensors

**Problema:** `start_fermentation_use_case.py` y `stop_fermentation_use_case.py` recibían `ISensorRepository` como dependencia para leer las últimas lecturas de cada sensor activo al iniciar/detener la fermentación. Los controllers importaban `SensorRepository` (implementación concreta).

**Solución:** Se agregaron dos métodos a `FermentationRepository` que consultan las tablas de sensores directamente vía SQL (son tablas de la misma DB compartida).

**Métodos agregados a `FermentationRepository`:**
- `get_latest_sensor_reading(circuit_id, sensor_type) -> float | None` — consulta la tabla del sensor correspondiente
- `get_active_sensors_for_circuit(circuit_id) -> list[str]` — consulta la tabla `circuits` para obtener los sensores activos

**Archivos modificados:**
- `src/services/fermentation/infrastructure/adapters/MySQL.py` — +2 métodos
- `src/services/fermentation/domain/repository.py` — +2 métodos abstractos en la interfaz
- `src/services/fermentation/application/usecase/start_fermentation_use_case.py` — elimina dependencia de `ISensorRepository` y `circuit`
- `src/services/fermentation/application/usecase/stop_fermentation_use_case.py` — igual
- `src/services/fermentation/infrastructure/controllers/start_fermentation_controller.py` — elimina imports de `SensorRepository` y `CircuitRepository`
- `src/services/fermentation/infrastructure/controllers/stop_fermentation_controller.py` — igual

---

### 2.3 fermentation → circuits

**Problema:** Los controllers de `start` y `stop` importaban `CircuitRepository` para obtener el objeto `Circuit` y llamar a `circuit.get_active_sensors()`. Resuelto en conjunto con el punto 2.2.

**Solución:** El método `get_active_sensors_for_circuit()` en `FermentationRepository` reemplaza la consulta al repositorio de circuits. Para `stop`, el `circuit_id` se obtiene directamente de `session.circuit_id`.

---

### 2.4 fermentation → auth

**Problema:** `FermentationRepository.get_user_id_by_circuit()` importaba `UserModel` de auth para buscar el dueño de un circuito y enviarle alertas de temperatura.

**Solución:** La consulta ahora busca en `fermentation_sessions WHERE circuit_id = ? AND status = 'running'`, que ya contiene el `user_id`. Además tiene más sentido semántico: la alerta va al usuario con la sesión activa, no al admin genérico del circuito.

**Archivos modificados:**
- `src/services/fermentation/infrastructure/adapters/MySQL.py` — método `get_user_id_by_circuit()` reescrito sin importar `UserModel`

---

### 2.5 users → circuits

**Problema:** `create_user_use_case.py` y `activate_my_circuit_use_case.py` importaban `ICircuitRepository` del servicio de circuits para validar el código de activación y activar el circuito. Los controllers importaban `CircuitRepository` (implementación concreta).

**Solución:** El servicio users define su propia interfaz `ICircuitLookup` con solo lo que necesita, implementada por un adapter que consulta la tabla `circuits` directamente vía SQL.

**Archivos nuevos:**
- `src/services/users/domain/entities/circuit_info.py` — dataclass mínimo con `id`, `is_active`, `created_at`
- `src/services/users/domain/circuit_lookup.py` — interfaz `ICircuitLookup` propia del servicio users
- `src/services/users/infrastructure/adapters/circuit_lookup_adapter.py` — implementación SQL sobre la tabla `circuits`

**Archivos modificados:**
- `src/services/users/application/usecase/create_user_use_case.py` — usa `ICircuitLookup` en vez de `ICircuitRepository`
- `src/services/users/application/usecase/activate_my_circuit_use_case.py` — igual
- `src/services/users/infrastructure/controllers/create_user_controller.py` — usa `CircuitLookupAdapter`
- `src/services/users/infrastructure/controllers/activate_circuit_controller.py` — igual

---

### 2.6 users → auth (modelos ORM compartidos)

**Problema:** `users/infrastructure/adapters/MySQL.py` importaba `UserModel` y `RoleModel` directamente desde `auth/infrastructure/adapters/MySQL.py`. Dos servicios compartían definiciones ORM desde el código de uno de ellos.

**Solución:** Los modelos ORM `UserModel` y `RoleModel` se movieron a `src/core/models/user_models.py` (patrón Shared Kernel). Tanto `auth` como `users` importan desde ahí.

**Justificación:** `src/core/` ya es la capa de infraestructura compartida del proyecto (`database.py`, `security.py`, `rabbitmq/`). Los modelos ORM de tablas usadas por múltiples servicios en una DB compartida pertenecen ahí.

**Archivos nuevos:**
- `src/core/models/__init__.py`
- `src/core/models/user_models.py` — `UserModel` y `RoleModel`

**Archivos modificados:**
- `src/services/auth/infrastructure/adapters/MySQL.py` — elimina definiciones de modelos, importa desde `core/models/`
- `src/services/users/infrastructure/adapters/MySQL.py` — elimina import desde auth, importa desde `core/models/`

---

## 3. Capa mapper en fermentation

**Problema:** `SENSOR_TABLE_MAP` y `SENSOR_REPORT_MAP` vivían dentro de `MySQL.py` mezclados con código ORM y SQL. Son constantes de configuración de esquema, no SQL.

**Solución:** Movidas a `src/services/fermentation/infrastructure/mappers/sensor_mappings.py`.

**Archivos nuevos:**
- `src/services/fermentation/infrastructure/mappers/__init__.py`
- `src/services/fermentation/infrastructure/mappers/sensor_mappings.py`

**Archivos modificados:**
- `src/services/fermentation/infrastructure/adapters/MySQL.py` — importa los mapas desde `mappers/`

---

## Resumen de acoplamientos

| # | Acoplamiento | Solución |
|---|---|---|
| 1 | sensors → fermentation | Evento RabbitMQ `sensor.deactivated` |
| 2 | fermentation → sensors | SQL directo en `FermentationRepository` |
| 3 | users → circuits | `ICircuitLookup` + `CircuitLookupAdapter` |
| 4 | fermentation → circuits | SQL directo en `FermentationRepository` |
| 5 | fermentation → auth | Consulta `fermentation_sessions` en vez de `UserModel` |
| 6 | users → auth | Modelos ORM movidos a `src/core/models/` |

---

## Impacto en el frontend

Ninguno. Todos los cambios son internos al backend:

- Los endpoints REST no cambiaron ni en ruta ni en contrato JSON
- Los mensajes WebSocket mantienen el mismo schema (se corrigió un bug en `SensorDeactivatedMessage` que usaba un campo inexistente)
- La autenticación JWT no cambió
- La única diferencia observable es que la actualización del reporte de fermentación al desactivar un sensor ahora ocurre a través de RabbitMQ (milisegundos de diferencia, imperceptible para el frontend)

---

## Arquitectura resultante

El proyecto es un **Monolito Modular con DB compartida y servicios desacoplados por contratos**. Es la arquitectura correcta para el tamaño del proyecto:

- DB única (MySQL) — sin overhead de múltiples instancias ni pérdida de integridad referencial
- Servicios sin importar código de infraestructura de otros servicios
- Comunicación interna por eventos RabbitMQ donde el desacoplamiento es necesario
- Comunicación por SQL directo donde los servicios acceden a tablas compartidas de la misma DB
