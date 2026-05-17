from src.core.exceptions import NotFoundException
from src.services.announcements.domain.entities.announcement import Announcement
from src.services.announcements.domain.repository import IAnnouncementRepository


class UpdateAnnouncementUseCase:

    def __init__(self, repository: IAnnouncementRepository):
        self._repo = repository

    async def execute(
        self,
        announcement_id: int,
        label:           str | None = None,
        version:         str | None = None,
        date:            str | None = None,
        title:           str | None = None,
        description:     str | None = None,
    ) -> Announcement:
        announcement = await self._repo.get_by_id(announcement_id)
        if not announcement:
            raise NotFoundException("Anuncio no encontrado")

        return await self._repo.update(
            announcement_id=announcement_id,
            label=label           or announcement.label,
            version=version       or announcement.version,
            date=date             or announcement.date,
            title=title           or announcement.title,
            description=description or announcement.description,
        )
