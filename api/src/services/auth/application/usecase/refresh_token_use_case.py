from src.core.exceptions import (
    SessionReplacedException,
    TokenInvalidException,
    UserNotFoundException,
)
from src.core.security import create_access_token, decode_token
from src.services.auth.domain.repository import IAuthRepository


class RefreshTokenUseCase:

    def __init__(self, repository: IAuthRepository):
        self._repo = repository

    async def execute(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)

        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalidException()

        user = await self._repo.get_user_by_id(int(user_id))
        if not user:
            raise UserNotFoundException()

        # ── Sesión única: el refresh debe pertenecer a la sesión activa ───────
        token_sid  = payload.get("sid")
        active_sid = await self._repo.get_active_session_id(int(user_id))
        if not token_sid or token_sid != active_sid:
            raise SessionReplacedException()

        # Se renueva el access token preservando la sesión (refresh no la rota).
        return {
            "access_token": create_access_token({
                "sub":        str(user.id),
                "role":       user.role.name if user.role else "estudiante",
                "circuit_id": user.circuit_id,
                "sid":        token_sid,
            }),
            "token_type": "bearer",
        }