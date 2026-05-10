"""
Simulador de sensores ESP32 → RabbitMQ (vía MQTT / amq.topic)

Flujo:
    1. Login con email + password → obtiene JWT
    2. POST /circuits/activate con activation_code → obtiene circuit_id
    3. Publica mensajes MQTT usando ese circuit_id

Uso:
    python simulate_sensors.py                                          # menú interactivo
    python simulate_sensors.py --circuit 1                              # con circuit_id directo
    python simulate_sensors.py --circuit 1 --session 2                 # con sesión activa
    python simulate_sensors.py --circuit 1 --session 2 --sensors temperature,ph
    python simulate_sensors.py --circuit 1 --session 2 --deactivate temperature
    python simulate_sensors.py --activate ABC123 --email u@x.com --password 1234
"""

import argparse
import asyncio
import json
import random
from datetime import datetime, timezone

import aio_pika
import httpx

# ── Configuración ─────────────────────────────────────────────────────────────
RABBITMQ_URL = "amqp://fabricio:Fabricio.2312@98.95.129.245:5672/"
EXCHANGE     = "amq.topic"
API_BASE_URL = "http://localhost:8000"   # ← cambia si tu backend corre en EC2

# ── Rangos realistas por sensor ───────────────────────────────────────────────
SENSOR_RANGES = {
    "temperature":  (18.0,  45.0),
    "ph":           (3.5,   7.5),
    "alcohol":      (0.0,   15.0),
    "density":      (0.990, 1.100),
    "conductivity": (0.5,   5.0),
    "turbidity":    (0.0,   100.0),
}

_sensor_state: dict[str, float] = {}


def _init_state():
    for sensor_type, (low, high) in SENSOR_RANGES.items():
        _sensor_state[sensor_type] = round(
            random.uniform(
                low + (high - low) * 0.3,
                low + (high - low) * 0.7,
            ), 3
        )


def _next_value(sensor_type: str) -> float:
    low, high = SENSOR_RANGES[sensor_type]
    rng       = high - low
    drift     = rng * 0.02
    current   = _sensor_state[sensor_type]
    new_value = current + random.uniform(-drift, drift)
    new_value = max(low, min(high, new_value))
    new_value = round(new_value, 3)
    _sensor_state[sensor_type] = new_value
    return new_value


# ── Auth & Activación ─────────────────────────────────────────────────────────

async def do_login(email: str, password: str, base_url: str = API_BASE_URL) -> str:
    """
    POST /auth/login → devuelve access_token (JWT).
    """
    print(f"\n  🔐 Autenticando como {email}...")
    async with httpx.AsyncClient(base_url=base_url) as client:
        resp = await client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        if resp.status_code != 200:
            print(f"  ❌ Login fallido ({resp.status_code}): {resp.text}")
            raise SystemExit(1)

        token = resp.json()["access_token"]
        print("  ✅ Login exitoso")
        return token


async def do_activate(activation_code: str, token: str, base_url: str = API_BASE_URL) -> int:
    """
    POST /circuits/activate → devuelve circuit_id.
    Solo es necesario llamarlo una vez (simula el primer arranque del ESP32).
    """
    print(f"\n  🔌 Activando circuito con código '{activation_code}'...")
    async with httpx.AsyncClient(base_url=base_url) as client:
        resp = await client.post(
            "/api/circuits/activate",
            json={"activation_code": activation_code},
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code != 200:
            print(f"  ❌ Activación fallida ({resp.status_code}): {resp.text}")
            raise SystemExit(1)

        circuit_id = resp.json()["id"]
        print(f"  ✅ Circuito activado → circuit_id={circuit_id}")
        return circuit_id


# ── RabbitMQ helpers ──────────────────────────────────────────────────────────

async def _get_exchange(channel):
    return await channel.get_exchange(EXCHANGE)


async def _publish(
    exchange,
    circuit_id:  int,
    sensor_type: str,
    value:       float,
    session_id:  int | None,
    active:      bool = True,
):
    routing_key = f"sensors.{circuit_id}.{sensor_type}"
    payload     = {
        "value":      value,
        "session_id": session_id,
        "active":     active,
        "timestamp":  datetime.now(timezone.utc).isoformat(),
    }
    message = aio_pika.Message(
        body=json.dumps(payload).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )
    await exchange.publish(message, routing_key=routing_key)

    status = "🟢 ACTIVO    " if active else "🔴 DESACTIVADO"
    print(
        f"  [{status}] {sensor_type:<15} "
        f"valor={str(value):<10} "
        f"circuit={circuit_id}  "
        f"session={session_id or '─'}"
    )


# ── Simulación continua ───────────────────────────────────────────────────────

async def simulate_continuous(
    circuit_id: int,
    session_id: int | None,
    sensors:    list[str],
    interval:   float,
    rounds:     int | None,
):
    print(f"\n{'─'*62}")
    print(f"  Conectando a RabbitMQ → {RABBITMQ_URL}")

    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel    = await connection.channel()
    exchange   = await _get_exchange(channel)

    print("  ✅ Conectado")
    print(f"  Circuit ID : {circuit_id}")
    print(f"  Session ID : {session_id or 'Sin sesión'}")
    print(f"  Sensores   : {', '.join(sensors)}")
    print(f"  Intervalo  : {interval}s")
    print(f"  Rondas     : {'∞  (Ctrl+C para detener)' if rounds is None else rounds}")
    print(f"{'─'*62}\n")

    _init_state()
    count = 0

    try:
        while rounds is None or count < rounds:
            count += 1
            print(f"📡 Ronda {count} — {datetime.now().strftime('%H:%M:%S')}")

            for sensor_type in sensors:
                value = _next_value(sensor_type)
                await _publish(
                    exchange=exchange,
                    circuit_id=circuit_id,
                    sensor_type=sensor_type,
                    value=value,
                    session_id=session_id,
                    active=True,
                )

            print()
            await asyncio.sleep(interval)

    except KeyboardInterrupt:
        print("\n⏹  Simulación detenida por el usuario")

    finally:
        await connection.close()
        print("🔌 Conexión cerrada\n")


async def simulate_deactivation(
    circuit_id:  int,
    session_id:  int,
    sensor_type: str,
):
    print(f"\n{'─'*62}")
    print(f"  Simulando desactivación de '{sensor_type}' en circuit={circuit_id}...")

    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel    = await connection.channel()
    exchange   = await _get_exchange(channel)

    _init_state()
    value = _next_value(sensor_type)

    await _publish(
        exchange=exchange,
        circuit_id=circuit_id,
        sensor_type=sensor_type,
        value=value,
        session_id=session_id,
        active=False,
    )

    await connection.close()
    print(f"{'─'*62}\n")


# ── Menú interactivo ──────────────────────────────────────────────────────────

async def interactive_menu():
    print("\n" + "═"*62)
    print("   🧪  SIMULADOR DE SENSORES ESP32 → RabbitMQ (MQTT)")
    print("═"*62)

    # ── Autenticación ─────────────────────────────────────────────────────────
    print("\n  [1/2] Autenticación o circuit_id directo")
    print("  ┌─ a) Autenticarse con email + password + activation_code")
    print("  └─ b) Ingresar circuit_id directamente (saltarse auth)")
    mode_auth = input("\n  Opción [a]: ").strip().lower() or "a"

    circuit_id: int

    if mode_auth == "a":
        email           = input("  Email: ").strip()
        password        = input("  Password: ").strip()
        activation_code = input("  Activation code: ").strip()

        token      = await do_login(email, password)
        circuit_id = await do_activate(activation_code, token)

    else:
        circuit_id = int(input("  Circuit ID: ").strip())

    # ── Session ───────────────────────────────────────────────────────────────
    session_raw = input("\n  Session ID (Enter para omitir): ").strip()
    session_id  = int(session_raw) if session_raw else None

    # ── Sensores ──────────────────────────────────────────────────────────────
    all_sensors = list(SENSOR_RANGES.keys())
    print("\n  Sensores disponibles:")
    for i, s in enumerate(all_sensors, 1):
        print(f"    {i}. {s}")
    print("    0. Todos")

    sensor_input = input("\n  Selecciona (ej: 1,3,5 o Enter para todos): ").strip()
    if not sensor_input or sensor_input == "0":
        sensors = all_sensors
    else:
        indices = [int(x.strip()) - 1 for x in sensor_input.split(",")]
        sensors = [all_sensors[i] for i in indices if 0 <= i < len(all_sensors)]

    # ── Modo ──────────────────────────────────────────────────────────────────
    print("\n  Modos:")
    print("    1. Continuo (Ctrl+C para detener)")
    print("    2. Rondas fijas")
    print("    3. Simular desactivación de un sensor")
    mode = input("\n  Modo [1]: ").strip() or "1"

    if mode == "3":
        if not session_id:
            session_id = int(input("  Session ID (requerido): ").strip())
        print("\n  Sensor a desactivar:")
        for i, s in enumerate(sensors, 1):
            print(f"    {i}. {s}")
        idx         = int(input("  Número: ").strip()) - 1
        sensor_type = sensors[idx]
        await simulate_deactivation(circuit_id, session_id, sensor_type)
        return

    interval = float(input("  Intervalo en segundos [2]: ").strip() or "2")
    rounds   = None
    if mode == "2":
        rounds = int(input("  Número de rondas [10]: ").strip() or "10")

    await simulate_continuous(
        circuit_id=circuit_id,
        session_id=session_id,
        sensors=sensors,
        interval=interval,
        rounds=rounds,
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(
        description="Simulador ESP32 → RabbitMQ (amq.topic / MQTT)"
    )

    # Auth flags (opcionales — si no se pasan se usa circuit directamente)
    parser.add_argument("--email",    type=str, default=None, help="Email para login")
    parser.add_argument("--password", type=str, default=None, help="Password para login")
    parser.add_argument("--activate", type=str, default=None, help="Activation code del circuito")

    # Flags directos (si ya tienes el circuit_id)
    parser.add_argument("--circuit",    type=int,   default=None, help="ID del circuito (omite auth)")
    parser.add_argument("--session",    type=int,   default=None, help="ID de sesión activa")
    parser.add_argument("--sensors",    type=str,   default=None, help="Sensores: temperature,ph,alcohol")
    parser.add_argument("--interval",   type=float, default=2.0,  help="Segundos entre rondas (default: 2)")
    parser.add_argument("--rounds",     type=int,   default=None, help="Número de rondas (default: infinito)")
    parser.add_argument("--deactivate", type=str,   default=None, help="Simula desactivación de un sensor")
    parser.add_argument("--api",        type=str,   default=API_BASE_URL, help=f"URL base del backend (default: {API_BASE_URL})")

    args = parser.parse_args()

    # Permite sobreescribir la URL base desde CLI
    base_url = args.api

    # Sin argumentos → menú interactivo
    if args.circuit is None and args.activate is None:
        await interactive_menu()
        return

    # ── Resolver circuit_id ───────────────────────────────────────────────────
    circuit_id: int

    if args.activate:
        if not args.email or not args.password:
            print("❌ --activate requiere --email y --password")
            return
        token      = await do_login(args.email, args.password, base_url)
        circuit_id = await do_activate(args.activate, token, base_url)

    else:
        circuit_id = args.circuit

    # ── Sensores ──────────────────────────────────────────────────────────────
    sensors = (
        [s.strip() for s in args.sensors.split(",")]
        if args.sensors
        else list(SENSOR_RANGES.keys())
    )

    # ── Desactivación ─────────────────────────────────────────────────────────
    if args.deactivate:
        if not args.session:
            print("❌ --deactivate requiere --session")
            return
        await simulate_deactivation(circuit_id, args.session, args.deactivate)
        return

    # ── Simulación continua ───────────────────────────────────────────────────
    await simulate_continuous(
        circuit_id=circuit_id,
        session_id=args.session,
        sensors=sensors,
        interval=args.interval,
        rounds=args.rounds,
    )


if __name__ == "__main__":
    asyncio.run(main())