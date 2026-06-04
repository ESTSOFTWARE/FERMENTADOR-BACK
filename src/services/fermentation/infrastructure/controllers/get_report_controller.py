from src.core.database import AsyncSessionLocal
from src.services.fermentation.application.usecase.get_report_use_case import GetReportUseCase
from src.services.fermentation.domain.dto.fermentation_report_schema import (
    FermentationReportResponse,
)
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository


async def get_report(session_id: int, user_id: int) -> FermentationReportResponse:
    repo = FermentationRepository(AsyncSessionLocal)
    return await GetReportUseCase(repo).execute(session_id, user_id)
