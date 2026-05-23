import asyncio

from src.core.database import AsyncSessionLocal
from src.services.announcements.application.usecase.create_announcement_use_case import (
    CreateAnnouncementUseCase,
)
from src.services.announcements.domain.dto.announcement_schema import CreateAnnouncementRequest
from src.services.announcements.infrastructure.adapters.MySQL import AnnouncementRepository
from src.services.notifications.application.usecase.send_notification_use_case import (
    SendNotificationUseCase,
)
from src.services.notifications.infrastructure.adapters.MySQL import NotificationRepository
from src.services.users.infrastructure.adapters.MySQL import UserRepository


async def create_announcement(body: CreateAnnouncementRequest, creator_id: int):
    repo         = AnnouncementRepository(AsyncSessionLocal)
    announcement = await CreateAnnouncementUseCase(repo).execute(
        label=body.label,
        version=body.version,
        title=body.title,
        description=body.description,
        date=body.date,
    )

    user_repo  = UserRepository(AsyncSessionLocal)
    notif_repo = NotificationRepository(AsyncSessionLocal)
    use_case   = SendNotificationUseCase(notif_repo)
    user_ids   = await user_repo.get_all_active_ids()

    await asyncio.gather(*[
        use_case.execute(
            user_id=uid,
            message=f"Nuevo comunicado: {body.title}",
            notification_type="new_announcement",
        )
        for uid in user_ids
        if uid != creator_id
    ])

    return announcement
