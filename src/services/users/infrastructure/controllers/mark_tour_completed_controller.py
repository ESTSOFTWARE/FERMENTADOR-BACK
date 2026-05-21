from src.core.database import AsyncSessionLocal
from src.services.users.application.usecase.mark_tour_completed_use_case import (
    MarkTourCompletedUseCase,
)
from src.services.users.infrastructure.adapters.MySQL import UserRepository


async def mark_tour_completed(user_id: int) -> dict:
    repo = UserRepository(AsyncSessionLocal)
    await MarkTourCompletedUseCase(repo).execute(user_id=user_id)
    return {"message": "Tour marcado como completado"}
