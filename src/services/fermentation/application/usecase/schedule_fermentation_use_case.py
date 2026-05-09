from datetime import datetime
from src.services.fermentation.domain.entities.fermentation_session import FermentationSession
from src.services.fermentation.domain.repository import IFermentationRepository
from src.core.exceptions import FermentationAlreadyRunningException, BadRequestException


class ScheduleFermentationUseCase:

    def __init__(self, repository: IFermentationRepository):
        self._repo = repository

    async def execute(
        self,
        circuit_id:      int,
        user_id:         int,
        scheduled_start: datetime,
        scheduled_end:   datetime,
        initial_sugar:   float,
    ) -> FermentationSession:
        if scheduled_end <= scheduled_start:
            raise BadRequestException(
                "La hora de fin debe ser mayor a la hora de inicio"
            )

        active = await self._repo.get_active_session_by_circuit(circuit_id)
        if active:
            raise FermentationAlreadyRunningException()

        session = await self._repo.create_session(
            circuit_id=circuit_id,
            user_id=user_id,
            formula_id=1,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
        )
        await self._repo.create_report(
            session_id=session.id,
            initial_sugar=initial_sugar,
        )
        return session