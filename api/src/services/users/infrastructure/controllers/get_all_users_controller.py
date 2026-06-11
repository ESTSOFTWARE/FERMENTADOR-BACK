from src.core.database import AsyncSessionLocal
from src.services.users.application.usecase.get_user_use_case import GetUserUseCase
from src.services.users.domain.dto.user_schema import UserResponse
from src.services.users.infrastructure.adapters.postgres import UserRepository


async def get_all(requester_id: int, requester_role: str) -> list[UserResponse]:
    repo = UserRepository(AsyncSessionLocal)
    users = await GetUserUseCase(repo).get_all(
        requester_id=requester_id,
        requester_role=requester_role,
    )
    return [UserResponse.from_entity(u) for u in users]


async def get_all_students() -> list[UserResponse]:
    repo  = UserRepository(AsyncSessionLocal)
    users = await GetUserUseCase(repo).get_all_students()
    return [UserResponse.from_entity(u) for u in users]
