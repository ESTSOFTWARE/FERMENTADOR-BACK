from src.services.fermentation.domain.entities.fermentation_session import FermentationSession
from src.services.fermentation.domain.repository import IFermentationRepository


class GetSessionsHistoryUseCase:

    def __init__(self, repository: IFermentationRepository):
        self._repo = repository

    async def execute(self, user_id: int, role: str) -> list[FermentationSession]:
        # Aislamiento por grupo: alumno ve las de sus grupos, maestra las suyas,
        # admin todas.
        return await self._repo.get_sessions_visible_to(user_id, role)