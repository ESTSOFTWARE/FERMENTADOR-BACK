from src.core.exceptions import NotFoundException
from src.services.announcements.domain.entities.announcement import Announcement
from src.services.announcements.domain.repository import IAnnouncementRepository


class GetAnnouncementByIdUseCase:

    def __init__(self, repository: IAnnouncementRepository):
        self._repo = repository

    async def execute(self, announcement_id: int) -> Announcement:
        announcement = await self._repo.get_by_id(announcement_id)
        if not announcement:
            raise NotFoundException("Anuncio no encontrado")
        return announcement
