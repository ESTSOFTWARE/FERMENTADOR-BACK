from src.core.database import AsyncSessionLocal
from src.services.fermentation.application.usecase.get_sessions_history_use_case import (
    GetSessionsHistoryUseCase,
)
from src.services.fermentation.domain.dto.fermentation_session_schema import (
    FermentationSessionResponse,
)
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository


async def get_sessions_history(user_id: int) -> list[FermentationSessionResponse]:
    repo = FermentationRepository(AsyncSessionLocal)
    sessions = await GetSessionsHistoryUseCase(repo).execute(user_id)
    return [FermentationSessionResponse.from_entity(s) for s in sessions]
