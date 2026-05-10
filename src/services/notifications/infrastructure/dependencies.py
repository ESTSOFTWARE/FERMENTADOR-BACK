from src.core.database import AsyncSessionLocal
from src.services.notifications.infrastructure.adapters.MySQL import NotificationRepository


def get_notification_repository() -> NotificationRepository:
    return NotificationRepository(AsyncSessionLocal)