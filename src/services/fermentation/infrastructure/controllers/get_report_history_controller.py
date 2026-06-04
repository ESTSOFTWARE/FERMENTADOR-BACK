from src.core.database import AsyncSessionLocal
from src.services.fermentation.application.usecase.get_report_history_use_case import (
    GetReportHistoryUseCase,
)
from src.services.fermentation.domain.dto.report_history_schema import ReportHistoryResponse
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository


async def get_report_history(user_id: int) -> list[ReportHistoryResponse]:
    repo = FermentationRepository(AsyncSessionLocal)
    return await GetReportHistoryUseCase(repo).execute(user_id)
