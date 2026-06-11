from src.core.exceptions import NotFoundException
from src.services.announcements.domain.entities.announcement import Announcement
from src.services.announcements.domain.repository import IAnnouncementRepository


class PinAnnouncementUseCase:

    def __init__(self, repository: IAnnouncementRepository):
        self._repo = repository

    async def execute(self, announcement_id: int, duration_days: int | None) -> Announcement:
        if not await self._repo.get_by_id(announcement_id):
            raise NotFoundException("Anuncio no encontrado")
        return await self._repo.pin(announcement_id, duration_days)
