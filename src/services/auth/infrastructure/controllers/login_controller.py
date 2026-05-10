from src.core.database import AsyncSessionLocal
from src.services.auth.application.usecase.login_use_case import LoginUseCase
from src.services.auth.domain.dto.login_schema import LoginRequest, TokenResponse
from src.services.auth.infrastructure.adapters.MySQL import AuthRepository


async def login(body: LoginRequest) -> TokenResponse:
    repo = AuthRepository(AsyncSessionLocal)
    return await LoginUseCase(repo).execute(email=body.email, password=body.password)
