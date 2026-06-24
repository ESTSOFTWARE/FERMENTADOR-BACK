from fastapi import Response

from src.core.database import AsyncSessionLocal
from src.core.exceptions import (
    FermentationReportNotFoundException,
    FermentationSessionNotFoundException,
)
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository
from src.services.fermentation.infrastructure.pdf.report_pdf import build_report_pdf


async def get_report_pdf(session_id: int) -> Response:
    repo = FermentationRepository(AsyncSessionLocal)

    session = await repo.get_session_by_id(session_id)
    if not session:
        raise FermentationSessionNotFoundException()

    report = await repo.get_report_by_session(session_id)
    if not report:
        raise FermentationReportNotFoundException()

    pdf_bytes = build_report_pdf(session, report)
    lote = f"F-{session.id:03d}"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="reporte_{lote}.pdf"'},
    )
