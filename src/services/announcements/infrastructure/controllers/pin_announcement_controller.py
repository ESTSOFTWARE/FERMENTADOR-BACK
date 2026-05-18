from src.core.database import AsyncSessionLocal
from src.services.announcements.application.usecase.pin_announcement_use_case import (
    PinAnnouncementUseCase,
)
from src.services.announcements.domain.entities.announcement import Announcement
from src.services.announcements.infrastructure.adapters.MySQL import AnnouncementRepository


async def pin_announcement(announcement_id: int, duration_days: int | None) -> Announcement:
    repo = AnnouncementRepository(AsyncSessionLocal)
    return await PinAnnouncementUseCase(repo).execute(announcement_id, duration_days)
