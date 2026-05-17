from src.services.announcements.domain.entities.announcement import Announcement
from src.services.announcements.domain.repository import IAnnouncementRepository


class GetAnnouncementsUseCase:

    def __init__(self, repository: IAnnouncementRepository):
        self._repo = repository

    async def execute(self) -> list[Announcement]:
        return await self._repo.get_all()
