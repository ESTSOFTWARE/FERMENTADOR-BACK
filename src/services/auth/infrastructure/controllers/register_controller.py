from src.core.database import AsyncSessionLocal
from src.services.auth.application.usecase.register_use_case import RegisterUseCase
from src.services.auth.domain.dto.register_schema import RegisterRequest, RegisterResponse
from src.services.auth.infrastructure.adapters.MySQL import AuthRepository


async def register(body: RegisterRequest) -> RegisterResponse:
    repo = AuthRepository(AsyncSessionLocal)
    return await RegisterUseCase(repo).execute(
        name=body.name,
        last_name=body.last_name,
        email=body.email,
        password=body.password,
    )
