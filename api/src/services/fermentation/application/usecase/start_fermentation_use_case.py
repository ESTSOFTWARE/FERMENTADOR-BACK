from datetime import datetime, timezone

from src.core.exceptions import (
    BadRequestException,
    FermentationAlreadyRunningException,
    FermentationSessionNotFoundException,
)
from src.core.threads.sensor_thread_manager import thread_manager
from src.core.websocket.sensor_audience import invalidate_audience
from src.services.fermentation.domain.entities.fermentation_session import FermentationSession
from src.services.fermentation.domain.repository import IFermentationRepository


class StartFermentationUseCase:

    def __init__(self, fermentation_repository: IFermentationRepository):
        self._fermentation_repo = fermentation_repository

    async def execute(self, session_id: int) -> FermentationSession:
        session = await self._fermentation_repo.get_session_by_id(session_id)
        if not session:
            raise FermentationSessionNotFoundException()

        if session.status == "running":
            raise FermentationAlreadyRunningException()

        if session.status != "scheduled":
            raise BadRequestException(
                f"No se puede iniciar una sesión en estado '{session.status}'"
            )

        now = datetime.now(timezone.utc).replace(tzinfo=None)  # naive para columnas sin zona

        session = await self._fermentation_repo.update_session_status(
            session_id=session_id,
            status="running",
            actual_start=now,
        )

        circuit_id     = session.circuit_id
        # La sesión ya está "running": fuerza recálculo de la audiencia del
        # circuito (ahora con el grupo de esta sesión).
        invalidate_audience(circuit_id)
        active_sensors = await self._fermentation_repo.get_active_sensors_for_circuit(circuit_id)

        for sensor_type in active_sensors:
            latest_value = await self._fermentation_repo.get_latest_sensor_reading(
                circuit_id=circuit_id,
                sensor_type=sensor_type,
            )
            if latest_value is not None:
                await self._fermentation_repo.update_sensor_initial(
                    session_id=session_id,
                    sensor_type=sensor_type,
                    value=latest_value,
                )

        thread_manager.start_session(
            circuit_id=circuit_id,
            session_id=session_id,
            active_sensors=active_sensors,
        )

        return session