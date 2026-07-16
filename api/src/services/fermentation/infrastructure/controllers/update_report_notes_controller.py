from src.core.database import AsyncSessionLocal
from src.services.fermentation.application.usecase.update_report_notes_use_case import (
    UpdateReportNotesUseCase,
)
from src.services.fermentation.domain.dto.fermentation_report_schema import (
    FermentationReportResponse,
)
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository


async def update_report_notes(
    session_id: int, notes: str, user_id: int,
) -> FermentationReportResponse:
    repo = FermentationRepository(AsyncSessionLocal)
    return await UpdateReportNotesUseCase(repo).execute(session_id, user_id, notes)
