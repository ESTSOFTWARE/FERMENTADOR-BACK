from src.services.fermentation.application.usecase.stop_fermentation_use_case import StopFermentationUseCase
from src.services.fermentation.infrastructure.adapters.MySQL import FermentationRepository
from src.services.fermentation.domain.dto.stop_fermentation_schema import StopFermentationRequest
from src.services.fermentation.domain.dto.fermentation_session_schema import FermentationSessionResponse
from src.core.database import AsyncSessionLocal


async def stop(session_id: int, body: StopFermentationRequest, user_id: int) -> FermentationSessionResponse:
    session = await StopFermentationUseCase(
        FermentationRepository(AsyncSessionLocal)
    ).execute(
        session_id     = session_id,
        interrupted_by = user_id if body.interrupted else None,
    )
    return FermentationSessionResponse.from_entity(session)
