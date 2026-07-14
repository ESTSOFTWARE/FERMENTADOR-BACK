from src.core.database import AsyncSessionLocal
from src.core.exceptions import TooManyRequestsException
from src.core.rate_limit import check_rate_limit
from src.services.auth.application.usecase.forgot_password_use_case import ForgotPasswordUseCase
from src.services.auth.domain.dto.password_reset_schema import ForgotPasswordRequest
from src.services.auth.infrastructure.adapters.postgres import AuthRepository


async def forgot_password(body: ForgotPasswordRequest) -> dict:
    if not check_rate_limit(f"forgot:{body.email}", max_requests=3, window_seconds=300):
        raise TooManyRequestsException()

    repo = AuthRepository(AsyncSessionLocal)
    await ForgotPasswordUseCase(repo).execute(body.email)
    # Mensaje genérico: no confirma si el correo está registrado.
    return {"message": "Si el correo está registrado, te enviamos un código"}
