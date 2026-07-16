import logging

from src.core.database import AsyncSessionLocal
from src.core.groq.recommendation_service import generate_report_notes
from src.services.fermentation.application.usecase.update_report_notes_use_case import (
    UpdateReportNotesUseCase,
)
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository

logger = logging.getLogger(__name__)


async def generate_notes(session_id: int, user_id: int) -> None:
    repo = FermentationRepository(AsyncSessionLocal)
    report = await repo.get_report_by_session(session_id)
    if not report:
        logger.warning("[NLP] Reporte no encontrado para sesión %s", session_id)
        return

    notes = generate_report_notes(report, session_id)
    try:
        await UpdateReportNotesUseCase(repo).execute(session_id, user_id, notes)
        logger.info("[NLP] Notas generadas y guardadas — session=%s", session_id)
    except Exception:
        logger.exception("[NLP] Error guardando notas — session=%s", session_id)
