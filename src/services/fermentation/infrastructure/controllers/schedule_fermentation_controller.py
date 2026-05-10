from src.core.database import AsyncSessionLocal
from src.services.fermentation.application.usecase.schedule_fermentation_use_case import (
    ScheduleFermentationUseCase,
)
from src.services.fermentation.domain.dto.fermentation_session_schema import (
    FermentationSessionResponse,
)
from src.services.fermentation.domain.dto.schedule_fermentation_schema import (
    ScheduleFermentationRequest,
)
from src.services.fermentation.infrastructure.adapters.MySQL import FermentationRepository


async def schedule(body: ScheduleFermentationRequest, user_id: int) -> FermentationSessionResponse:
    repo = FermentationRepository(AsyncSessionLocal)
    session = await ScheduleFermentationUseCase(repo).execute(
        circuit_id      = body.circuit_id,
        user_id         = user_id,
        scheduled_start = body.scheduled_start,
        scheduled_end   = body.scheduled_end,
        initial_sugar   = body.initial_sugar,
    )
    return FermentationSessionResponse.from_entity(session)
