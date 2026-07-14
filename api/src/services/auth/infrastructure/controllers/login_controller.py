from fastapi import Request, Response

from src.core.cookie_manager import set_auth_cookies
from src.core.database import AsyncSessionLocal
from src.core.exceptions import TooManyRequestsException
from src.core.rate_limit import check_rate_limit
from src.services.auth.application.usecase.login_use_case import LoginUseCase
from src.services.auth.domain.dto.login_schema import LoginRequest
from src.services.auth.infrastructure.adapters.postgres import AuthRepository


def _client_ip(request: Request) -> str:
    # Detrás del proxy de Railway la IP real viene en X-Forwarded-For.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def login(body: LoginRequest, response: Response, request: Request) -> dict:
    # Anti fuerza bruta: limita intentos por correo y por IP (5 min de ventana).
    ip = _client_ip(request)
    if not check_rate_limit(f"login:email:{body.email}", max_requests=8, window_seconds=300):
        raise TooManyRequestsException()
    if not check_rate_limit(f"login:ip:{ip}", max_requests=30, window_seconds=300):
        raise TooManyRequestsException()

    repo   = AuthRepository(AsyncSessionLocal)
    result = await LoginUseCase(repo).execute(email=body.email, password=body.password)
    set_auth_cookies(response, result["access_token"], result["refresh_token"])
    return {
        "access_token":  result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type":    result["token_type"],
        "user":          result["user"],
    }
