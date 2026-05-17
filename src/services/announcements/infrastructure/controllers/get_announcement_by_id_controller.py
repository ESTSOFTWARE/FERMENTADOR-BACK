from src.core.database import AsyncSessionLocal
from src.services.announcements.application.usecase.get_announcement_by_id_use_case import (
    GetAnnouncementByIdUseCase,
)
from src.services.announcements.infrastructure.adapters.MySQL import AnnouncementRepository


async def get_announcement_by_id(announcement_id: int):
    repo = AnnouncementRepository(AsyncSessionLocal)
    return await GetAnnouncementByIdUseCase(repo).execute(announcement_id)
