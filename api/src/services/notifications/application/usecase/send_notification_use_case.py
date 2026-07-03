from datetime import datetime, timezone

from src.core.rabbitmq.ws_events import to_users
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

        notif_msg = NotificationMessage(
            type=notification_type,
            notification_id=notification.id,
            message=message,
            session_id=session_id,
            occurred_at=notification.created_at or datetime.now(timezone.utc),
        )

        # In-process (transición): solo si hay conexión local al /ws de este back.
        if ws_manager.is_user_connected(user_id):
            await ws_manager.broadcast_notification(
                user_id=user_id,
                message=notif_msg,
            )

        # RabbitMQ → ws-service (Node): siempre. El cliente puede estar conectado
        # al Node (vía gateway), no al manager in-process. `data` = lo que ya
        # recibía el front (mismo shape que model_dump_json).
        await to_users("notifications", [user_id], notif_msg.model_dump(mode="json"))

        # Push FCM (app cerrada / segundo plano). Best-effort: no rompe si falla.
        try:
            from src.core.fcm.fcm_service import send_push_to_user
            await send_push_to_user(
                user_id=user_id,
                title="Nich-Ká",
                body=message,
                data={"type": notification_type, "notification_id": notification.id},
            )
        except Exception:  # noqa: BLE001
            pass

        return notification.id