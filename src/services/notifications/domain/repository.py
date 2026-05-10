from abc import ABC, abstractmethod

from src.services.notifications.domain.entities.notification import Notification


class INotificationRepository(ABC):

    @abstractmethod
    async def create(
        self,
        user_id:    int,
        message:    str,
        notif_type: str,
        session_id: int | None = None,
    ) -> Notification:
        ...

    @abstractmethod
    async def get_by_user(
        self,
        user_id:     int,
        only_unread: bool = False,
    ) -> list[Notification]:
        ...

    @abstractmethod
    async def mark_as_read(self, notification_id: int) -> Notification | None:
        ...

    @abstractmethod
    async def mark_all_as_read(self, user_id: int) -> None:
        ...