from dataclasses import replace

from src.core.exceptions import FermentationReportNotFoundException
from src.services.fermentation.domain.entities.fermentation_report import FermentationReport
from src.services.fermentation.domain.repository import IFermentationRepository


class UpdateReportNotesUseCase:
    """Guarda la nota generada por el NLP en el reporte de una sesión.

    Mantiene el mismo criterio de acceso que `GetReportUseCase`: si el usuario
    puede leer el reporte (require_any_role + reporte existente), puede
    actualizar su nota.
    """

    def __init__(self, repository: IFermentationRepository):
        self._repo = repository

    async def execute(
        self, session_id: int, user_id: int, notes: str,
    ) -> FermentationReport:
        report = await self._repo.get_report_by_session(session_id)
        if not report:
            raise FermentationReportNotFoundException()

        updated = await self._repo.update_report(replace(report, notes=notes))
        await self._repo.create_report_history(
            report_id=report.id,
            user_id=user_id,
            action="notes_updated",
        )
        return updated
