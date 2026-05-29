from fastapi import APIRouter, Request, Response

from src.services.auth.domain.dto.login_schema import (
    LoginCookieResponse,
    LoginRequest,
    TokenResponse,
)
from src.services.auth.domain.dto.oauth_schema import GoogleMobileRequest
from src.services.auth.domain.dto.password_reset_schema import (
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
)
from src.services.auth.domain.dto.register_schema import RegisterRequest, RegisterResponse
from src.services.auth.infrastructure.controllers.forgot_password_controller import (
    forgot_password,
)
from src.services.auth.infrastructure.controllers.github_web_controller import github_redirect
from src.services.auth.infrastructure.controllers.google_mobile_controller import google_mobile
from src.services.auth.infrastructure.controllers.google_web_controller import google_redirect
from src.services.auth.infrastructure.controllers.login_controller import login
from src.services.auth.infrastructure.controllers.logout_controller import logout
from src.services.auth.infrastructure.controllers.refresh_token_controller import refresh_token
from src.services.auth.infrastructure.controllers.register_controller import register
from src.services.auth.infrastructure.controllers.reset_password_controller import reset_password

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    summary="Registrar nuevo administrador",
)
async def register_route(body: RegisterRequest):
    return await register(body)


@router.post(
    "/login",
    response_model=LoginCookieResponse,
    summary="Iniciar sesión (establece HttpOnly cookies)",
)
async def login_route(body: LoginRequest, response: Response):
    return await login(body, response)


@router.post(
    "/refresh",
    response_model=MessageResponse,
    summary="Renovar access token desde cookie",
)
async def refresh_route(request: Request, response: Response):
    return await refresh_token(request, response)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Cerrar sesión y limpiar cookies",
)
async def logout_route(response: Response):
    return await logout(response)


@router.get("/google", summary="Iniciar OAuth con Google (web admin)")
async def google_redirect_route():
    return await google_redirect()


@router.get("/github", summary="Iniciar OAuth con GitHub (web admin)")
async def github_redirect_route():
    return await github_redirect()


@router.post(
    "/google/mobile",
    response_model=TokenResponse,
    summary="Login con Google para app móvil (ID Token desde SDK)",
)
async def google_mobile_route(body: GoogleMobileRequest):
    return await google_mobile(body)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Solicitar código de recuperación de contraseña",
)
async def forgot_password_route(body: ForgotPasswordRequest):
    return await forgot_password(body)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Verificar código y cambiar contraseña",
)
async def reset_password_route(body: ResetPasswordRequest):
    return await reset_password(body)
