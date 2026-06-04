import logging

from fastapi import Request, Response

from src.core.cookie_manager import clear_auth_cookies
from src.core.database import AsyncSessionLocal
from src.core.security import decode_token
from src.services.auth.infrastructure.adapters.postgres import AuthRepository

logger = logging.getLogger(__name__)


async def logout(request: Request, response: Response) -> dict:
    # Invalidar la sesión activa en BD (best-effort: no debe fallar el logout).
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
            if user_id:
                await AuthRepository(AsyncSessionLocal).clear_active_session(int(user_id))
        except Exception:
            # Token expirado/inválido: la sesión ya no es válida, solo limpiamos cookies.
            logger.debug("[Auth] Logout con token inválido o expirado; se limpian cookies.")

    clear_auth_cookies(response)
    return {"message": "Sesión cerrada correctamente"}
