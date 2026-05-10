from fastapi import APIRouter

from src.services.auth.domain.dto.login_schema import LoginRequest, TokenResponse
from src.services.auth.domain.dto.oauth_schema import GoogleMobileRequest
from src.services.auth.domain.dto.refresh_token_schema import (
    AccessTokenResponse,
    RefreshTokenRequest,
)
from src.services.auth.domain.dto.register_schema import RegisterRequest, RegisterResponse
from src.services.auth.infrastructure.controllers.github_web_controller import (
    github_callback,
    github_redirect,
)
from src.services.auth.infrastructure.controllers.google_mobile_controller import google_mobile
from src.services.auth.infrastructure.controllers.google_web_controller import (
    google_callback,
    google_redirect,
)
from src.services.auth.infrastructure.controllers.login_controller import login
from src.services.auth.infrastructure.controllers.refresh_token_controller import refresh_token
from src.services.auth.infrastructure.controllers.register_controller import register

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    summary="Registrar nuevo administrador",
)
async def register_route(body: RegisterRequest):
    return await register(body)


@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión")
async def login_route(body: LoginRequest):
    return await login(body)


@router.post("/refresh", response_model=AccessTokenResponse, summary="Refrescar access token")
async def refresh_route(body: RefreshTokenRequest):
    return await refresh_token(body)


@router.get("/google", summary="Iniciar OAuth con Google (web admin)")
async def google_redirect_route():
    return await google_redirect()


@router.get("/callback/google", summary="Callback Google OAuth → redirige al frontend con tokens")
async def google_callback_route(code: str):
    return await google_callback(code)


@router.get("/github", summary="Iniciar OAuth con GitHub (web admin)")
async def github_redirect_route():
    return await github_redirect()


@router.get("/callback/github", summary="Callback GitHub OAuth → redirige al frontend con tokens")
async def github_callback_route(code: str):
    return await github_callback(code)


@router.post(
    "/google/mobile",
    response_model=TokenResponse,
    summary="Login con Google para app móvil (ID Token desde SDK)",
)
async def google_mobile_route(body: GoogleMobileRequest):
    return await google_mobile(body)
