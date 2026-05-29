from fastapi import Response

from src.core.cookie_manager import set_auth_cookies
from src.core.database import AsyncSessionLocal
from src.services.auth.application.usecase.login_use_case import LoginUseCase
from src.services.auth.domain.dto.login_schema import LoginRequest
from src.services.auth.infrastructure.adapters.MySQL import AuthRepository


async def login(body: LoginRequest, response: Response) -> dict:
    repo   = AuthRepository(AsyncSessionLocal)
    result = await LoginUseCase(repo).execute(email=body.email, password=body.password)
    set_auth_cookies(response, result["access_token"], result["refresh_token"])
    return {"user": result["user"]}
