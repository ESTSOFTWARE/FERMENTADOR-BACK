from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

from src.services.auth.domain.dto.delete_account_schema import DeleteAccountRequest
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
from src.services.auth.infrastructure.controllers.delete_account_controller import (
    request_account_deletion,
)
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
    response_model=TokenResponse,
    summary="Iniciar sesión (establece HttpOnly cookies y devuelve tokens en body)",
)
async def login_route(body: LoginRequest, response: Response, request: Request):
    return await login(body, response, request)


@router.post(
    "/refresh",
    response_model=MessageResponse,
    summary="Renovar access token desde cookie",
)
async def refresh_route(request: Request, response: Response):
    return await refresh_token(request, response)


class MobileRefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh/mobile", summary="Renovar access token (móvil: refresh en el body)")
async def refresh_mobile_route(body: MobileRefreshRequest):
    from src.core.database import AsyncSessionLocal
    from src.services.auth.application.usecase.refresh_token_use_case import RefreshTokenUseCase
    from src.services.auth.infrastructure.adapters.postgres import AuthRepository

    result = await RefreshTokenUseCase(AuthRepository(AsyncSessionLocal)).execute(body.refresh_token)
    return {"access_token": result["access_token"]}


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Cerrar sesión y limpiar cookies",
)
async def logout_route(request: Request, response: Response):
    return await logout(request, response)


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


@router.post(
    "/delete-account-request",
    summary="Solicitar eliminación de cuenta (público, sin autenticación)",
)
async def delete_account_request_route(body: DeleteAccountRequest):
    return await request_account_deletion(body)
