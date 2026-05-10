from src.core.database import AsyncSessionLocal
from src.services.users.application.usecase.update_user_use_case import UpdateUserUseCase
from src.services.users.domain.dto.update_user_schema import UpdateUserRequest
from src.services.users.domain.dto.user_schema import UserResponse
from src.services.users.infrastructure.adapters.MySQL import UserRepository


async def update(user_id: int, body: UpdateUserRequest) -> UserResponse:
    repo = UserRepository(AsyncSessionLocal)
    user = await UpdateUserUseCase(repo).execute(
        user_id=user_id,
        name=body.name,
        last_name=body.last_name,
        email=body.email,
        password=body.password,
        role=body.role,
        profile_image=body.profile_image,
    )
    return UserResponse.from_entity(user)
