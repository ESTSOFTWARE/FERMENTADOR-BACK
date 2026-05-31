"""
Reset de contraseña. Siempre escribe el nuevo hash en Argon2,
independientemente del hash anterior del usuario.
"""

import logging

from src.core.email.email_service import send_password_changed_email
from src.core.exceptions import InvalidResetCodeException, UserNotFoundException
from src.core.security import hash_password          # ahora es Argon2
from src.services.auth.domain.repository import IAuthRepository

logger = logging.getLogger(__name__)


class ResetPasswordUseCase:

    def __init__(self, repository: IAuthRepository):
        self._repo = repository

    async def execute(self, email: str, code: str, new_password: str) -> None:
        user = await self._repo.get_user_by_email(email)
        if not user:
            raise UserNotFoundException()

        is_valid = await self._repo.get_valid_reset_code(user.id, code)
        if not is_valid:
            raise InvalidResetCodeException()

        hashed = hash_password(new_password)         # Argon2id
        await self._repo.update_password(user.id, hashed)
        await self._repo.invalidate_reset_codes(user.id)
        await send_password_changed_email(to_email=user.email, name=user.name)
        logger.info("[ResetPassword] Contraseña actualizada para usuario id=%s", user.id)