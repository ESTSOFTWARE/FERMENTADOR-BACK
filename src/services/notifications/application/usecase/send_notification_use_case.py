from datetime import datetime, timezone

from src.core.websocket.schemas import NotificationMessage
from src.core.websocket.websocket_manager import ws_manager
from src.services.notifications.domain.repository import INotificationRepository


class SendNotificationUseCase:

    def __init__(self, repository: INotificationRepository):
        self._repo = repository

    async def execute(
        self,
        user_id:           int,
        message:           str,
        notification_type: str,
        session_id:        int | None = None,
    ) -> int:
        notification = await self._repo.create(
            user_id=user_id,
            message=message,
            notif_type=notification_type,
            session_id=session_id,
        )

        if ws_manager.is_user_connected(user_id):
            notif_msg = NotificationMessage(
                type=notification_type,
                notification_id=notification.id,
                message=message,
                session_id=session_id,
                occurred_at=notification.created_at or datetime.now(timezone.utc),
            )
            await ws_manager.broadcast_notification(
                user_id=user_id,
                message=notif_msg,
            )

        return notification.id