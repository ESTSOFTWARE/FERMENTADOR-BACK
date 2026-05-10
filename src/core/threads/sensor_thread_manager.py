import logging

from src.core.config import settings
from src.core.threads.base_sensor_thread import BaseSensorThread

logger = logging.getLogger(__name__)


class SensorThreadManager:
    """
    Gestiona el ciclo de vida de los hilos de sensores por circuito.

    Estructura interna:
    {
        circuit_id: {
            "alcohol":      SensorThread,
            "density":      SensorThread,
            "conductivity": SensorThread,
            "ph":           SensorThread,
            "temperature":  SensorThread,
            "turbidity":    SensorThread,
        }
    }

    Un hilo por sensor por circuito. Si hay 3 circuitos activos
    con 6 sensores cada uno → 18 hilos corriendo en paralelo.
    """

    def __init__(self):
        # circuit_id → { sensor_type → thread }
        self._threads: dict[int, dict[str, BaseSensorThread]] = {}
        # Clase concreta que se usará para crear los hilos
        # Se inyecta desde main.py para evitar imports circulares
        self._thread_class: type[BaseSensorThread] | None = None

    def set_thread_class(self, thread_class: type[BaseSensorThread]) -> None:
        """
        Inyecta la clase concreta de hilo a usar.
        Se llama desde main.py al arrancar la app.
        """
        self._thread_class = thread_class
        logger.info(
            f"[ThreadManager] Clase de hilo configurada → {thread_class.__name__}"
        )

    # ── Arranque de fermentación ──────────────────────────────────────────────
    def start_session(
        self,
        circuit_id: int,
        session_id: int,
        active_sensors: list[str],
    ) -> None:
        """
        Levanta un hilo por cada sensor activo al iniciar una fermentación.

        Args:
            circuit_id:      ID del circuito
            session_id:      ID de la sesión de fermentación activa
            active_sensors:  Lista de sensores activos
                             ej: ["alcohol", "ph", "temperature"]
        """
        if not self._thread_class:
            raise RuntimeError(
                "[ThreadManager] No se configuró la clase de hilo. "
                "Llama a set_thread_class() primero."
            )

        if circuit_id in self._threads:
            logger.warning(
                f"[ThreadManager] Ya existen hilos para circuit_id={circuit_id}. "
                f"Deteniéndolos antes de iniciar nuevos."
            )
            self.stop_session(circuit_id)

        self._threads[circuit_id] = {}

        for sensor_type in active_sensors:
            if sensor_type not in settings.SENSOR_TYPES:
                logger.warning(
                    f"[ThreadManager] Tipo de sensor desconocido → {sensor_type}"
                )
                continue

            thread = self._thread_class(
                circuit_id=circuit_id,
                session_id=session_id,
                sensor_type=sensor_type,
            )
            thread.start()
            self._threads[circuit_id][sensor_type] = thread

        logger.info(
            f"[ThreadManager] Sesión iniciada → "
            f"circuit_id={circuit_id} | "
            f"session_id={session_id} | "
            f"sensores={active_sensors}"
        )

    # ── Fin de fermentación ───────────────────────────────────────────────────
    def stop_session(self, circuit_id: int) -> None:
        """
        Detiene todos los hilos de un circuito al terminar la fermentación.

        Args:
            circuit_id: ID del circuito a detener
        """
        if circuit_id not in self._threads:
            logger.warning(
                f"[ThreadManager] No hay hilos activos para circuit_id={circuit_id}"
            )
            return

        sensor_threads = self._threads.pop(circuit_id)

        for sensor_type, thread in sensor_threads.items():
            try:
                thread.stop()
                logger.info(
                    f"[ThreadManager] Hilo detenido → "
                    f"sensor={sensor_type} | circuit_id={circuit_id}"
                )
            except Exception as e:
                logger.error(
                    f"[ThreadManager] Error al detener hilo → "
                    f"sensor={sensor_type} | circuit_id={circuit_id} | error={e}"
                )

        logger.info(
            f"[ThreadManager] Sesión detenida → circuit_id={circuit_id}"
        )

    # ── Control individual de sensores ────────────────────────────────────────
    def stop_sensor(self, circuit_id: int, sensor_type: str) -> None:
        """
        Detiene el hilo de un sensor específico sin afectar los demás.
        Se usa cuando se desactiva un sensor individual durante la fermentación.

        Args:
            circuit_id:  ID del circuito
            sensor_type: Tipo de sensor a detener
        """
        circuit_threads = self._threads.get(circuit_id)
        if not circuit_threads:
            logger.warning(
                f"[ThreadManager] No hay hilos para circuit_id={circuit_id}"
            )
            return

        thread = circuit_threads.get(sensor_type)
        if not thread:
            logger.warning(
                f"[ThreadManager] No hay hilo para "
                f"sensor={sensor_type} | circuit_id={circuit_id}"
            )
            return

        thread.stop()
        del circuit_threads[sensor_type]

        logger.info(
            f"[ThreadManager] Sensor detenido individualmente → "
            f"sensor={sensor_type} | circuit_id={circuit_id}"
        )

    def start_sensor(
        self,
        circuit_id: int,
        session_id: int,
        sensor_type: str,
    ) -> None:
        """
        Levanta el hilo de un sensor específico sin afectar los demás.
        Se usa cuando se reactiva un sensor durante la fermentación.

        Args:
            circuit_id:  ID del circuito
            session_id:  ID de la sesión activa
            sensor_type: Tipo de sensor a iniciar
        """
        if not self._thread_class:
            raise RuntimeError(
                "[ThreadManager] No se configuró la clase de hilo."
            )

        if circuit_id not in self._threads:
            self._threads[circuit_id] = {}

        if sensor_type in self._threads[circuit_id]:
            existing = self._threads[circuit_id][sensor_type]
            if existing.is_running():
                logger.warning(
                    f"[ThreadManager] El sensor ya tiene un hilo activo → "
                    f"sensor={sensor_type} | circuit_id={circuit_id}"
                )
                return

        thread = self._thread_class(
            circuit_id=circuit_id,
            session_id=session_id,
            sensor_type=sensor_type,
        )
        thread.start()
        self._threads[circuit_id][sensor_type] = thread

        logger.info(
            f"[ThreadManager] Sensor reactivado → "
            f"sensor={sensor_type} | circuit_id={circuit_id}"
        )

    # ── Helpers ───────────────────────────────────────────────────────────────
    def stop_all(self) -> None:
        """
        Detiene todos los hilos de todos los circuitos.
        Se llama al apagar la app desde main.py.
        """
        circuit_ids = list(self._threads.keys())
        for circuit_id in circuit_ids:
            self.stop_session(circuit_id)
        logger.info("[ThreadManager] Todos los hilos detenidos")

    def get_active_sensors(self, circuit_id: int) -> list[str]:
        """Retorna la lista de sensores con hilo activo para un circuito."""
        circuit_threads = self._threads.get(circuit_id, {})
        return [
            sensor_type
            for sensor_type, thread in circuit_threads.items()
            if thread.is_running()
        ]

    def get_active_circuits(self) -> list[int]:
        """Retorna la lista de circuit_ids con hilos activos."""
        return [
            circuit_id
            for circuit_id, threads in self._threads.items()
            if any(t.is_running() for t in threads.values())
        ]

    def is_session_running(self, circuit_id: int) -> bool:
        """Verifica si hay una sesión activa para un circuito."""
        circuit_threads = self._threads.get(circuit_id, {})
        return any(t.is_running() for t in circuit_threads.values())

    def get_thread_count(self) -> int:
        """Retorna el total de hilos activos en el sistema."""
        return sum(
            1
            for threads in self._threads.values()
            for thread in threads.values()
            if thread.is_running()
        )


# ── Instancia global ──────────────────────────────────────────────────────────
thread_manager = SensorThreadManager()