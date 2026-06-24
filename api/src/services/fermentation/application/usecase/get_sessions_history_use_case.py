from src.services.fermentation.domain.entities.fermentation_session import FermentationSession
from src.services.fermentation.domain.repository import IFermentationRepository


class GetSessionsHistoryUseCase:

    def __init__(self, repository: IFermentationRepository):
        self._repo = repository

    async def execute(self, circuit_id: int) -> list[FermentationSession]:
        # Historial por circuito: el estudiante ve las fermentaciones de su
        # fermentador, no solo las que él creó.
        return await self._repo.get_sessions_by_circuit(circuit_id)