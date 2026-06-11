from src.core.database import AsyncSessionLocal
from src.services.announcements.application.usecase.delete_announcement_use_case import (
    DeleteAnnouncementUseCase,
)
from src.services.announcements.infrastructure.adapters.postgres import AnnouncementRepository


async def delete_announcement(announcement_id: int) -> None:
    repo = AnnouncementRepository(AsyncSessionLocal)
    await DeleteAnnouncementUseCase(repo).execute(announcement_id)
