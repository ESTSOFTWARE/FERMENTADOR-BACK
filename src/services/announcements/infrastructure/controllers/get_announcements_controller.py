from src.core.database import AsyncSessionLocal
from src.services.announcements.application.usecase.get_announcements_use_case import (
    GetAnnouncementsUseCase,
)
from src.services.announcements.infrastructure.adapters.postgres import AnnouncementRepository


async def get_announcements() -> list:
    repo = AnnouncementRepository(AsyncSessionLocal)
    return await GetAnnouncementsUseCase(repo).execute()
