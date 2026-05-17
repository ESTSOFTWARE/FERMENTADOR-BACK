from src.core.exceptions import NotFoundException
from src.services.announcements.domain.repository import IAnnouncementRepository


class DeleteAnnouncementUseCase:

    def __init__(self, repository: IAnnouncementRepository):
        self._repo = repository

    async def execute(self, announcement_id: int) -> None:
        if not await self._repo.get_by_id(announcement_id):
            raise NotFoundException("Anuncio no encontrado")
        await self._repo.delete(announcement_id)
