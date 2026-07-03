import enum

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    select,
    text,
    update,
)

from src.core.database import Base
from src.services.notifications.domain.entities.notification import Notification
from src.services.notifications.domain.repository import INotificationRepository


# ── Enums ─────────────────────────────────────────────────────────────────────
class NotificationTypeEnum(str, enum.Enum):
    FERMENTATION_STARTED     = "fermentation_started"
    FERMENTATION_COMPLETE    = "fermentation_complete"
    FERMENTATION_INTERRUPTED = "fermentation_interrupted"
    HIGH_TEMPERATURE         = "high_temperature"
    SENSOR_FAILURE           = "sensor_failure"
    NEW_ANNOUNCEMENT         = "new_announcement"
    MEMBER_ADDED             = "member_added"
    MEMBER_REMOVED           = "member_removed"
    USER_REGISTERED          = "user_registered"
    EXPERIMENT_COMPLETE      = "experiment_complete"
    GENERAL                  = "general"


class NotificationStatusEnum(str, enum.Enum):
    UNREAD = "unread"
    READ   = "read"


# ── Modelo ORM ────────────────────────────────────────────────────────────────
class NotificationModel(Base):
    __tablename__  = "notifications"
    __table_args__ = {"extend_existing": True}

    id         = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("fermentation_sessions.id"), nullable=True)
    type       = Column(String(50), nullable=False, default="general")
    message    = Column(Text, nullable=False)
    status     = Column(String(10), nullable=False, default="unread")
    created_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )


class DeviceTokenModel(Base):
    """Token FCM por dispositivo/usuario para notificaciones push."""
    __tablename__  = "device_tokens"
    __table_args__ = {"extend_existing": True}

    id         = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token      = Column(String(255), nullable=False, unique=True)
    platform   = Column(String(20), nullable=False, default="android")
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


# ── Repositorio ───────────────────────────────────────────────────────────────
class NotificationRepository(INotificationRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def create(
        self,
        user_id:    int,
        message:    str,
        notif_type: str,
        session_id: int | None = None,
    ) -> Notification:
        async with self._session_factory() as session:
            model = NotificationModel(
                user_id=user_id,
                message=message,
                type=notif_type,
                session_id=session_id,
                status="unread",
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def get_by_user(
        self,
        user_id:     int,
        only_unread: bool = False,
    ) -> list[Notification]:
        async with self._session_factory() as session:
            query = (
                select(NotificationModel)
                .where(NotificationModel.user_id == user_id)
                .order_by(NotificationModel.created_at.desc())
            )
            if only_unread:
                query = query.where(NotificationModel.status == "unread")

            result = await session.execute(query)
            return [self._to_entity(m) for m in result.scalars().all()]

    async def mark_as_read(self, notification_id: int) -> Notification | None:
        async with self._session_factory() as session:
            await session.execute(
                update(NotificationModel)
                .where(NotificationModel.id == notification_id)
                .values(status="read")
            )
            await session.commit()

            result = await session.execute(
                select(NotificationModel)
                .where(NotificationModel.id == notification_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def mark_all_as_read(self, user_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(NotificationModel)
                .where(
                    NotificationModel.user_id == user_id,
                    NotificationModel.status == "unread",
                )
                .values(status="read")
            )
            await session.commit()

    def _to_entity(self, model: NotificationModel) -> Notification:
        return Notification(
            id=model.id,
            user_id=model.user_id,
            message=model.message,
            type=model.type,
            status=model.status,
            session_id=model.session_id,
            created_at=model.created_at,
        )