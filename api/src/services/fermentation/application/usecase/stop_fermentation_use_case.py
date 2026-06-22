from datetime import datetime, timezone

from src.core.exceptions import (
    FermentationNotRunningException,
    FermentationSessionNotFoundException,
)
from src.core.threads.sensor_thread_manager import thread_manager
from src.core.websocket.sensor_audience import invalidate_audience
from src.services.fermentation.domain.entities.fermentation_session import FermentationSession
from src.services.fermentation.domain.repository import IFermentationRepository


class StopFermentationUseCase:

    def __init__(self, fermentation_repository: IFermentationRepository):
        self._fermentation_repo = fermentation_repository

    async def execute(
        self,
        session_id:     int,
        interrupted_by: int | None = None,
    ) -> FermentationSession:
        session = await self._fermentation_repo.get_session_by_id(session_id)
        if not session:
            raise FermentationSessionNotFoundException()

        if session.status != "running":
            raise FermentationNotRunningException()

        now        = datetime.now(timezone.utc).replace(tzinfo=None)  # naive para columnas sin zona
        status     = "interrupted" if interrupted_by else "completed"
        circuit_id = session.circuit_id

        active_sensors = thread_manager.get_active_sensors(circuit_id)
        for sensor_type in active_sensors:
            latest_value = await self._fermentation_repo.get_latest_sensor_reading(
                circuit_id=circuit_id,
                sensor_type=sensor_type,
            )
            if latest_value is not None:
                await self._fermentation_repo.update_sensor_final(
                    session_id=session_id,
                    sensor_type=sensor_type,
                    value=latest_value,
                )

        await self._calculate_efficiency(session_id)

        session = await self._fermentation_repo.update_session_status(
            session_id=session_id,
            status=status,
            actual_end=now,
            interrupted_by=interrupted_by,
        )

        report = await self._fermentation_repo.get_report_by_session(session_id)
        if report:
            await self._fermentation_repo.create_report_history(
                report_id=report.id,
                user_id=session.user_id,
                action="generated",
            )

        thread_manager.stop_session(circuit_id)
        # Ya no hay sesión corriendo: la audiencia vuelve a "todos" en la próxima lectura.
        invalidate_audience(circuit_id)
        return session

    async def _calculate_efficiency(self, session_id: int) -> None:
        report = await self._fermentation_repo.get_report_by_session(session_id)
        if not report:
            return

        factor              = await self._fermentation_repo.get_active_formula_factor()
        ethanol_detected    = report.alcohol_final or report.alcohol_last_reading
        theoretical_ethanol = report.initial_sugar * factor
        efficiency          = None

        if ethanol_detected and theoretical_ethanol > 0:
            efficiency = min(
                100.0,
                round((ethanol_detected / theoretical_ethanol) * 100, 2)
            )

        report.ethanol_detected    = ethanol_detected
        report.theoretical_ethanol = theoretical_ethanol
        report.efficiency          = efficiency
        await self._fermentation_repo.update_report(report)