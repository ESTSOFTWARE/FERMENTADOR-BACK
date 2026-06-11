from src.core.database import AsyncSessionLocal
from src.services.auth.application.usecase.reset_password_use_case import ResetPasswordUseCase
from src.services.auth.domain.dto.password_reset_schema import ResetPasswordRequest
from src.services.auth.infrastructure.adapters.postgres import AuthRepository


async def reset_password(body: ResetPasswordRequest) -> dict:
    repo = AuthRepository(AsyncSessionLocal)
    await ResetPasswordUseCase(repo).execute(body.email, body.code, body.new_password)
    return {"message": "Contraseña actualizada correctamente"}
