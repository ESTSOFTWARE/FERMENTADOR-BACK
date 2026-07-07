from fastapi import APIRouter, Depends

from src.core.dependencies import require_admin_or_profesor, require_any_role, require_feature
from src.services.fermentation.domain.dto.fermentation_report_schema import (
    FermentationReportResponse,
)
from src.services.fermentation.domain.dto.fermentation_session_schema import (
    FermentationSessionResponse,
)
from src.services.fermentation.domain.dto.report_history_schema import ReportHistoryResponse
from src.services.fermentation.domain.dto.schedule_fermentation_schema import (
    ScheduleFermentationRequest,
)
from src.services.fermentation.domain.dto.session_with_report_schema import (
    SessionWithReportResponse,
)
from src.services.fermentation.domain.dto.stop_fermentation_schema import StopFermentationRequest
from src.services.fermentation.infrastructure.controllers.get_active_session_controller import (
    get_active,
)
from src.services.fermentation.infrastructure.controllers.get_report_controller import get_report
from src.services.fermentation.infrastructure.controllers.get_report_history_controller import (
    get_report_history,
)
from src.services.fermentation.infrastructure.controllers.get_report_pdf_controller import (
    get_report_pdf,
)
from src.services.fermentation.infrastructure.controllers.get_sessions_history_controller import (
    get_sessions_history,
)
from src.services.fermentation.infrastructure.controllers.get_sessions_with_reports_controller import (
    get_sessions_with_reports,
)
from src.services.fermentation.infrastructure.controllers.schedule_fermentation_controller import (
    schedule,
)
from src.services.fermentation.infrastructure.controllers.start_fermentation_controller import start
from src.services.fermentation.infrastructure.controllers.stop_fermentation_controller import stop

router = APIRouter()


@router.post(
    "/schedule",
    response_model=FermentationSessionResponse,
    status_code=201,
    summary="Programar fermentación",
)
async def schedule_fermentation(
    body: ScheduleFermentationRequest,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await schedule(body, current_user["user_id"])


@router.get(
    "/active",
    response_model=FermentationSessionResponse | None,
    summary="Sesión activa del circuito del usuario",
)
async def get_active_session(current_user: dict = Depends(require_any_role)):
    return await get_active(current_user.get("circuit_id"), current_user.get("user_id"))


@router.get(
    "/sessions",
    response_model=list[FermentationSessionResponse],
    summary="Historial de sesiones del usuario",
)
async def get_sessions_history_route(current_user: dict = Depends(require_any_role)):
    return await get_sessions_history(current_user["user_id"], current_user["role"])


@router.get(
    "/sessions-with-reports",
    response_model=list[SessionWithReportResponse],
    summary="Sesiones + su reporte en una sola consulta (evita el N+1)",
)
async def get_sessions_with_reports_route(current_user: dict = Depends(require_any_role)):
    return await get_sessions_with_reports(current_user["user_id"], current_user["role"])


@router.get(
    "/history",
    response_model=list[ReportHistoryResponse],
    summary="Historial de reportes del usuario",
)
async def get_report_history_route(current_user: dict = Depends(require_any_role)):
    return await get_report_history(current_user["user_id"])


@router.post(
    "/{session_id}/start",
    response_model=FermentationSessionResponse,
    summary="Iniciar fermentación",
)
async def start_fermentation(
    session_id: int,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await start(session_id)


@router.post(
    "/{session_id}/stop",
    response_model=FermentationSessionResponse,
    summary="Detener fermentación",
)
async def stop_fermentation(
    session_id: int,
    body: StopFermentationRequest,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await stop(session_id, body, current_user["user_id"])


@router.get(
    "/{session_id}/report",
    response_model=FermentationReportResponse,
    summary="Obtener reporte de una sesión",
)
async def get_report_route(
    session_id: int,
    current_user: dict = Depends(require_any_role),
):
    return await get_report(session_id, current_user["user_id"])


@router.get(
    "/{session_id}/report/pdf",
    summary="Descargar el reporte de una sesión en PDF",
)
async def get_report_pdf_route(
    session_id: int,
    current_user: dict = Depends(require_feature("reports")),
):
    return await get_report_pdf(session_id)
