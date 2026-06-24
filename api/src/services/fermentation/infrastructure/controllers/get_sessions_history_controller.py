from src.core.database import AsyncSessionLocal
from src.services.fermentation.application.usecase.get_sessions_history_use_case import (
    GetSessionsHistoryUseCase,
)
from src.services.fermentation.domain.dto.fermentation_session_schema import (
    FermentationSessionResponse,
)
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository


async def get_sessions_history(circuit_id=None, user_id=None) -> list[FermentationSessionResponse]:
    repo = FermentationRepository(AsyncSessionLocal)

    # Igual que /active: si el token no trae circuit_id, lo resolvemos del usuario.
    if not circuit_id and user_id is not None:
        try:
            from src.services.auth.infrastructure.adapters.postgres import AuthRepository
            user       = await AuthRepository(AsyncSessionLocal).get_user_by_id(user_id)
            circuit_id = getattr(user, "circuit_id", None) if user else None
        except Exception:
            circuit_id = None

    if not circuit_id:
        return []

    sessions = await GetSessionsHistoryUseCase(repo).execute(circuit_id)
    return [FermentationSessionResponse.from_entity(s) for s in sessions]
