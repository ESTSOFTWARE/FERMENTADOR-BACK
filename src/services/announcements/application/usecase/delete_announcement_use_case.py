from src.core.exceptions import NotFoundException
from src.services.announcements.domain.repository import IAnnouncementRepository


class DeleteAnnouncementUseCase:

    def __init__(self, repository: IAnnouncementRepository):
        self._repo = repository

    async def execute(self, announcement_id: int) -> None:
        announcements = await self._repo.get_all()
        if not any(a.id == announcement_id for a in announcements):
            raise NotFoundException("Anuncio no encontrado")
        await self._repo.delete(announcement_id)
