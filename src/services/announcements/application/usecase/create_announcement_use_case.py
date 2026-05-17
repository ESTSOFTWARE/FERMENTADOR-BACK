from datetime import datetime

from src.services.announcements.domain.entities.announcement import Announcement
from src.services.announcements.domain.repository import IAnnouncementRepository

_MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


def _current_date_label() -> str:
    now = datetime.now()
    return f"{_MESES[now.month]} {now.year}"


class CreateAnnouncementUseCase:

    def __init__(self, repository: IAnnouncementRepository):
        self._repo = repository

    async def execute(
        self,
        label:       str,
        version:     str,
        title:       str,
        description: str,
        date:        str | None = None,
    ) -> Announcement:
        return await self._repo.create(
            label=label,
            version=version,
            date=date or _current_date_label(),
            title=title,
            description=description,
        )
