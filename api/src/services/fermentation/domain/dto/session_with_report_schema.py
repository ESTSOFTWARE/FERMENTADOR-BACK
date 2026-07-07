from pydantic import BaseModel

from src.services.fermentation.domain.dto.fermentation_report_schema import (
    FermentationReportResponse,
)
from src.services.fermentation.domain.dto.fermentation_session_schema import (
    FermentationSessionResponse,
)


class SessionWithReportResponse(BaseModel):
    """Sesión + su reporte (o None). Permite traer todo en una sola petición."""

    session: FermentationSessionResponse
    report:  FermentationReportResponse | None
