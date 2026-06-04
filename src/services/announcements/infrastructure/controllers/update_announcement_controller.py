from src.core.database import AsyncSessionLocal
from src.services.announcements.application.usecase.update_announcement_use_case import (
    UpdateAnnouncementUseCase,
)
from src.services.announcements.domain.dto.announcement_schema import UpdateAnnouncementRequest
from src.services.announcements.infrastructure.adapters.postgres import AnnouncementRepository


async def update_announcement(announcement_id: int, body: UpdateAnnouncementRequest):
    repo = AnnouncementRepository(AsyncSessionLocal)
    return await UpdateAnnouncementUseCase(repo).execute(
        announcement_id=announcement_id,
        label=body.label,
        version=body.version,
        date=body.date,
        title=body.title,
        description=body.description,
    )
