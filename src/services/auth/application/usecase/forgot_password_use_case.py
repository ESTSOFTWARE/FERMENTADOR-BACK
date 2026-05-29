import logging
import secrets
from datetime import datetime, timedelta, timezone

from src.core.email.email_service import send_reset_password_email
from src.core.exceptions import UserNotFoundException
from src.services.auth.domain.repository import IAuthRepository

logger = logging.getLogger(__name__)

EXPIRATION_MINUTES = 15


class ForgotPasswordUseCase:

    def __init__(self, repository: IAuthRepository):
        self._repo = repository

    async def execute(self, email: str) -> None:
        user = await self._repo.get_user_by_email(email)
        if not user:
            raise UserNotFoundException()

        code = str(secrets.randbelow(900000) + 100000)
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            minutes=EXPIRATION_MINUTES
        )

        await self._repo.save_reset_code(user.id, code, expires_at)
        await send_reset_password_email(to_email=user.email, name=user.name, code=code)
        logger.info(f"[ForgotPassword] Código enviado a {email}")
