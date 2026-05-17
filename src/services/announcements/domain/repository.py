from abc import ABC, abstractmethod

from src.services.announcements.domain.entities.announcement import Announcement


class IAnnouncementRepository(ABC):

    @abstractmethod
    async def get_all(self) -> list[Announcement]: ...

    @abstractmethod
    async def create(
        self,
        label:       str,
        version:     str,
        date:        str,
        title:       str,
        description: str,
    ) -> Announcement: ...

    @abstractmethod
    async def delete(self, announcement_id: int) -> None: ...
