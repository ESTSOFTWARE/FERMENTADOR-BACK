from src.core.database import AsyncSessionLocal
from src.services.users.application.usecase.delete_user_use_case import DeleteUserUseCase
from src.services.users.infrastructure.adapters.postgres import UserRepository


async def delete(user_id: int) -> None:
    repo = UserRepository(AsyncSessionLocal)
    await DeleteUserUseCase(repo).execute(user_id)
