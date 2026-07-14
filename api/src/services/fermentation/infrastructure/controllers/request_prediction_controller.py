import asyncio
import logging

from src.core.database import AsyncSessionLocal
from src.core.ml.ml_client import forward_reading
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository
from src.services.sensors.infrastructure.adapters.postgres import SensorRepository

logger = logging.getLogger(__name__)


async def request_prediction(session_id: int) -> None:
    ferm_repo   = FermentationRepository(AsyncSessionLocal)
    sensor_repo = SensorRepository(AsyncSessionLocal)

    session = await ferm_repo.get_session_by_id(session_id)
    if session is None:
        raise ValueError(f"Sesión {session_id} no encontrada.")

    asyncio.create_task(
        forward_reading(
            circuit_id=session.circuit_id,
            session_id=session.id,
            actual_start=session.actual_start,
            scheduled_start=session.scheduled_start,
            scheduled_end=session.scheduled_end,
            sensor_repo=sensor_repo,
            force=True,
        )
    )
    logger.info("[ML] Predicción manual solicitada → session=%s circuit=%s", session.id, session.circuit_id)
