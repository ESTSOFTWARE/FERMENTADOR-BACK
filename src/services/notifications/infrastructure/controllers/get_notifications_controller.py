from src.core.database import AsyncSessionLocal
from src.services.notifications.domain.dto.notification_schema import NotificationResponse
from src.services.notifications.infrastructure.adapters.MySQL import NotificationRepository


async def get_all(user_id: int, only_unread: bool) -> list[NotificationResponse]:
    repo = NotificationRepository(AsyncSessionLocal)
    notifications = await repo.get_by_user(user_id=user_id, only_unread=only_unread)
    return [NotificationResponse.from_entity(n) for n in notifications]
