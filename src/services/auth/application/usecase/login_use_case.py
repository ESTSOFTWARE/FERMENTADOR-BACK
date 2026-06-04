"""
Flujo de login con migración automática bcrypt → Argon2:
1. Buscar usuario por email.
2. Detectar tipo de hash (bcrypt / Argon2).
3. Validar contraseña con el verificador correspondiente.
4. Si el hash es bcrypt (o Argon2 desactualizado): rehashear con Argon2 y persistir.
5. Retornar tokens JWT.
"""

import logging

from src.core.exceptions import InvalidCredentialsException
from src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    needs_rehash,
    verify_password,
)
from src.core.session import rotate_and_revoke
from src.services.auth.domain.repository import IAuthRepository

logger = logging.getLogger(__name__)


class LoginUseCase:

    def __init__(self, repository: IAuthRepository):
        self._repo = repository

    async def execute(self, email: str, password: str) -> dict:
        user = await self._repo.get_user_by_email(email)

        if not user:
            raise InvalidCredentialsException()

        if not user.password or not verify_password(password, user.password):
            raise InvalidCredentialsException()

        # ── Migración progresiva bcrypt → Argon2 ──────────────────────────────
        # Se ejecuta de forma transparente tras un login exitoso.
        # El usuario no percibe ningún cambio; la contraseña en BD se actualiza silenciosamente al formato Argon2.
        if needs_rehash(user.password):
            try:
                new_hash = hash_password(password)
                await self._repo.update_password(user.id, new_hash)
                logger.info(
                    "[Auth] Hash migrado a Argon2 para usuario id=%s", user.id
                )
            except Exception:
                # No bloquear el login si la migración falla.
                # El usuario seguirá con bcrypt y se reintentará en el próximo login.
                logger.warning(
                    "[Auth] No se pudo migrar el hash de usuario id=%s", user.id,
                    exc_info=True,
                )

        # ── Construir tokens ──────────────────────────────────────────────────
        role_name = user.role.name if user.role else "estudiante"

        # ── Sesión única: nueva sesión invalida + expulsa la anterior ─────────
        sid = await rotate_and_revoke(self._repo, user.id)

        token_data = {
            "sub":        str(user.id),
            "role":       role_name,
            "circuit_id": user.circuit_id,
            "sid":        sid,
        }

        if user.oauth_google_id:
            provider = "google"
        elif user.oauth_github_id:
            provider = "github"
        else:
            provider = "email"

        return {
            "access_token":  create_access_token(token_data),
            "refresh_token": create_refresh_token({"sub": str(user.id), "sid": sid}),
            "token_type":    "bearer",
            "user": {
                "id":             user.id,
                "name":           user.name,
                "last_name":      user.last_name,
                "email":          user.email,
                "role":           role_name,
                "circuit_id":     user.circuit_id,
                "profile_image":  user.profile_image,
                "oauth_provider": provider,
            },
        }