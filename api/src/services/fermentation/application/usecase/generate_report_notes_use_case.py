import logging

from src.core.nlp.nlp_client import generate_notes
from src.services.fermentation.domain.dto.fermentation_report_schema import (
    FermentationReportResponse,
)
from src.services.fermentation.domain.repository import IFermentationRepository

logger = logging.getLogger(__name__)


class GenerateReportNotesUseCase:
    """Pide la nota al NLP y la guarda en el reporte.

    Se dispara al terminar la fermentación, tanto si la detuvo un usuario
    como si expiró sola (auto-stop). Corre fire-and-forget: cualquier fallo
    se registra y se ignora.
    """

    def __init__(self, fermentation_repository: IFermentationRepository):
        self._fermentation_repo = fermentation_repository

    async def execute(self, session_id: int) -> None:
        report = await self._fermentation_repo.get_report_by_session(session_id)
        if not report:
            logger.warning("[NLP] Sin reporte para la sesión %s; no hay nota", session_id)
            return

        payload = FermentationReportResponse.model_validate(
            report, from_attributes=True
        ).model_dump(mode="json")

        notes = await generate_notes(payload)
        if not notes:
            return

        report.notes = notes
        await self._fermentation_repo.update_report(report)
        logger.info("[NLP] Nota generada y guardada — session=%s", session_id)
