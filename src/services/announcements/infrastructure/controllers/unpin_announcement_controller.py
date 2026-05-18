from src.core.database import AsyncSessionLocal
from src.services.announcements.application.usecase.unpin_announcement_use_case import (
    UnpinAnnouncementUseCase,
)
from src.services.announcements.domain.entities.announcement import Announcement
from src.services.announcements.infrastructure.adapters.MySQL import AnnouncementRepository


async def unpin_announcement(announcement_id: int) -> Announcement:
    repo = AnnouncementRepository(AsyncSessionLocal)
    return await UnpinAnnouncementUseCase(repo).execute(announcement_id)
