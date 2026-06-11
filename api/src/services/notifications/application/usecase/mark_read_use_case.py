from src.services.notifications.domain.entities.notification import Notification
from src.services.notifications.domain.repository import INotificationRepository


class MarkReadUseCase:

    def __init__(self, repository: INotificationRepository):
        self._repo = repository

    async def execute_one(self, notification_id: int) -> Notification | None:
        return await self._repo.mark_as_read(notification_id)

    async def execute_all(self, user_id: int) -> None:
        await self._repo.mark_all_as_read(user_id)