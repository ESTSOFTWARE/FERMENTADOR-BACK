from src.core.database import AsyncSessionLocal
from src.services.notifications.application.usecase.mark_read_use_case import MarkReadUseCase
from src.services.notifications.infrastructure.adapters.postgres import NotificationRepository


async def mark_all_as_read(user_id: int) -> None:
    repo = NotificationRepository(AsyncSessionLocal)
    await MarkReadUseCase(repo).execute_all(user_id)
