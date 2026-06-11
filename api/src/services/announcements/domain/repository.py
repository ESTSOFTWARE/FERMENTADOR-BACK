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
    async def get_by_id(self, announcement_id: int) -> Announcement | None: ...

    @abstractmethod
    async def update(
        self,
        announcement_id: int,
        label:           str,
        version:         str,
        date:            str,
        title:           str,
        description:     str,
    ) -> Announcement: ...

    @abstractmethod
    async def delete(self, announcement_id: int) -> None: ...

    @abstractmethod
    async def pin(self, announcement_id: int, duration_days: int | None) -> Announcement: ...

    @abstractmethod
    async def unpin(self, announcement_id: int) -> Announcement: ...
