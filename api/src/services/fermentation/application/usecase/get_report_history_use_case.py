from src.services.fermentation.domain.entities.report_history import ReportHistory
from src.services.fermentation.domain.repository import IFermentationRepository


class GetReportHistoryUseCase:

    def __init__(self, repository: IFermentationRepository):
        self._repo = repository

    async def execute(self, user_id: int) -> list[ReportHistory]:
        return await self._repo.get_report_history_by_user(user_id)
    