from src.core.exceptions import FermentationReportNotFoundException
from src.services.fermentation.domain.entities.fermentation_report import FermentationReport
from src.services.fermentation.domain.repository import IFermentationRepository


class GetReportUseCase:

    def __init__(self, repository: IFermentationRepository):
        self._repo = repository

    async def execute(self, session_id: int, user_id: int) -> FermentationReport:
        report = await self._repo.get_report_by_session(session_id)
        if not report:
            raise FermentationReportNotFoundException()

        await self._repo.create_report_history(
            report_id=report.id,
            user_id=user_id,
            action="viewed",
        )
        return report