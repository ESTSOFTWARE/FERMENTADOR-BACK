from src.services.fermentation.domain.entities.fermentation_session import FermentationSession
from src.services.fermentation.domain.repository import IFermentationRepository


class GetSessionsHistoryUseCase:

    def __init__(self, repository: IFermentationRepository):
        self._repo = repository

    async def execute(self, user_id: int) -> list[FermentationSession]:
        return await self._repo.get_sessions_by_user(user_id)