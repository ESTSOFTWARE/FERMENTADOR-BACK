from fastapi import Response

from src.core.database import AsyncSessionLocal
from src.core.exceptions import (
    FermentationReportNotFoundException,
    FermentationSessionNotFoundException,
)
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository
from src.services.fermentation.infrastructure.pdf.report_pdf import build_report_pdf
from src.services.users.infrastructure.adapters.postgres import UserRepository


async def get_report_pdf(session_id: int) -> Response:
    repo = FermentationRepository(AsyncSessionLocal)

    session = await repo.get_session_by_id(session_id)
    if not session:
        raise FermentationSessionNotFoundException()

    report = await repo.get_report_by_session(session_id)
    if not report:
        raise FermentationReportNotFoundException()

    # Dueño + código de activación (el repo de usuarios llena circuit_code).
    owner_name   = None
    owner_role   = None
    circuit_code = None
    try:
        owner = await UserRepository(AsyncSessionLocal).get_by_id(session.user_id)
        if owner:
            owner_name   = f"{owner.name} {owner.last_name}".strip()
            owner_role   = owner.role_name
            circuit_code = owner.circuit_code
    except Exception:  # noqa: BLE001 — datos extra, no debe romper el PDF
        pass

    pdf_bytes = build_report_pdf(
        session, report,
        owner_name=owner_name, owner_role=owner_role, circuit_code=circuit_code,
    )
    lote = f"F-{session.id:03d}"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="fermentacion-{lote}.pdf"'},
    )
