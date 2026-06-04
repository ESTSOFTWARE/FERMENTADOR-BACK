"""
Manejo centralizado del identificador de sesión única por usuario.

Cada login genera un session_id nuevo que se persiste en users.active_session_id
y se embebe en el JWT como claim "sid". Las requests autenticadas comparan el
"sid" del token contra el de la BD; si no coincide, la sesión fue reemplazada
por otra más reciente → 401.
"""
import uuid

SESSION_CLAIM = "sid"


def new_session_id() -> str:
    """Genera un identificador de sesión único (uuid4 hex, 32 chars)."""
    return uuid.uuid4().hex


async def rotate_and_revoke(repo, user_id: int) -> str:
    """
    Inicia una nueva sesión para el usuario:
    1. Genera un session_id nuevo y lo persiste (invalida la sesión anterior).
    2. Empuja `session:revoked` por WebSocket a las conexiones previas para
       expulsarlas al instante (sin esperar a su próxima request).

    Devuelve el nuevo session_id para embeberlo en el JWT.
    """
    from src.core.websocket.session_ws_manager import session_ws_manager

    sid = new_session_id()
    await repo.set_active_session(user_id, sid)
    await session_ws_manager.revoke(user_id)
    return sid
