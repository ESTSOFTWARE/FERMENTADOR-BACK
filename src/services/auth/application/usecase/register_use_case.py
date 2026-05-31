"""
Registro de nuevos usuarios. Siempre usa Argon2 para el hash inicial.
"""

from src.core.email.email_service import send_welcome_email
from src.core.exceptions import EmailAlreadyExistsException
from src.core.security import hash_password
from src.services.auth.domain.repository import IAuthRepository

ADMIN_ROLE_ID = 1


class RegisterUseCase:

    def __init__(self, repository: IAuthRepository):
        self._repo = repository

    async def execute(
        self,
        name:         str,
        last_name:    str,
        email:        str,
        password:     str,
        dial_code:    str | None = None,
        phone_number: str | None = None,
    ) -> dict:
        existing = await self._repo.get_user_by_email(email)
        if existing:
            raise EmailAlreadyExistsException()

        hashed = hash_password(password)          # Argon2id

        user = await self._repo.create_user(
            name=name,
            last_name=last_name,
            email=email,
            password=hashed,
            role_id=ADMIN_ROLE_ID,
            circuit_id=None,
            dial_code=dial_code,
            phone_number=phone_number,
        )

        await send_welcome_email(to_email=user.email, name=user.name)

        return {
            "id":        user.id,
            "name":      user.name,
            "last_name": user.last_name,
            "email":     user.email,
            "role":      user.role.name if user.role else "admin",
        }