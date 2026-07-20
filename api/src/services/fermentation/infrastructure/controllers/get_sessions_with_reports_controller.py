from src.core.database import AsyncSessionLocal
from src.services.fermentation.domain.dto.fermentation_report_schema import (
    FermentationReportResponse,
)
from src.services.fermentation.domain.dto.fermentation_session_schema import (
    FermentationSessionResponse,
)
from src.services.fermentation.domain.dto.session_with_report_schema import (
    SessionWithReportResponse,
)
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository


async def get_sessions_with_reports(
    user_id: int, role: str, limit: int | None = None
) -> list[SessionWithReportResponse]:
    repo = FermentationRepository(AsyncSessionLocal)
    pairs = await repo.get_sessions_with_reports_visible_to(user_id, role, limit)
    return [
        SessionWithReportResponse(
            session=FermentationSessionResponse.from_entity(s),
            report=(
                FermentationReportResponse.model_validate(r, from_attributes=True)
                if r else None
            ),
        )
        for s, r in pairs
    ]
