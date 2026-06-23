"""
Auto-detiene las fermentaciones cuyo scheduled_end ya pasó.

Se ejecuta periódicamente (tarea de fondo en main.py). Para cada sesión
'running' vencida: la marca como 'completed' (reusa StopFermentationUseCase) y
publica el comando "todo apagado" al ESP32 vía RabbitMQ → MQTT.
"""
import logging
from datetime import datetime, timezone

from src.core.rabbitmq.publisher import publisher
from src.services.fermentation.application.usecase.stop_fermentation_use_case import (
    StopFermentationUseCase,
)
from src.services.fermentation.domain.repository import IFermentationRepository

logger = logging.getLogger(__name__)

# Estado "todo apagado" que se manda al circuito al terminar (mismas llaves que el front).
_OFF_STATE = {
    "motor":                "apagado",
    "bomba":                "apagado",
    "sensor_temperatura":   "apagado",
    "sensor_ph":            "apagado",
    "sensor_alcohol":       "apagado",
    "sensor_conductividad": "apagado",
    "sensor_turbidez":      "apagado",
}


class AutoStopExpiredFermentationsUseCase:

    def __init__(self, fermentation_repository: IFermentationRepository):
        self._repo = fermentation_repository
        self._stop = StopFermentationUseCase(fermentation_repository)

    async def execute(self) -> int:
        now     = datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC (columnas sin zona)
        expired = await self._repo.get_running_sessions_past_end(now)
        stopped = 0
        for s in expired:
            try:
                await self._stop.execute(s.id)        # sin interrupted_by → "completed"
                await self._publish_off(s.circuit_id)
                stopped += 1
            except Exception as e:  # noqa: BLE001 — una sesión no debe romper las demás
                logger.error(f"[AutoStop] Error deteniendo sesión {s.id}: {e}")
        return stopped

    async def _publish_off(self, circuit_id: int) -> None:
        try:
            await publisher.publish_raw(
                exchange="amq.topic",
                routing_key=f"commands.{circuit_id}.state",
                payload=_OFF_STATE,
            )
        except Exception as e:  # noqa: BLE001 — best-effort (el broker puede fallar)
            logger.warning(
                f"[AutoStop] No se pudieron apagar los dispositivos del circuito {circuit_id}: {e}"
            )
