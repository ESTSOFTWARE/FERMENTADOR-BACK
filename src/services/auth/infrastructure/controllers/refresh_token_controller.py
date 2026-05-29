from fastapi import Request, Response

from src.core.cookie_manager import set_access_cookie
from src.core.database import AsyncSessionLocal
from src.core.exceptions import TokenInvalidException
from src.services.auth.application.usecase.refresh_token_use_case import RefreshTokenUseCase
from src.services.auth.infrastructure.adapters.MySQL import AuthRepository


async def refresh_token(request: Request, response: Response) -> dict:
    token = request.cookies.get("refresh_token")
    if not token:
        raise TokenInvalidException()

    repo   = AuthRepository(AsyncSessionLocal)
    result = await RefreshTokenUseCase(repo).execute(token)
    set_access_cookie(response, result["access_token"])
    return {"message": "Token renovado"}
