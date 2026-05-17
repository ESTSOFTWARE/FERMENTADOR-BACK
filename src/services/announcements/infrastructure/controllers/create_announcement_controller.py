from src.core.database import AsyncSessionLocal
from src.services.announcements.application.usecase.create_announcement_use_case import (
    CreateAnnouncementUseCase,
)
from src.services.announcements.domain.dto.announcement_schema import CreateAnnouncementRequest
from src.services.announcements.infrastructure.adapters.MySQL import AnnouncementRepository


async def create_announcement(body: CreateAnnouncementRequest):
    repo = AnnouncementRepository(AsyncSessionLocal)
    return await CreateAnnouncementUseCase(repo).execute(
        label=body.label,
        version=body.version,
        title=body.title,
        description=body.description,
        date=body.date,
    )
