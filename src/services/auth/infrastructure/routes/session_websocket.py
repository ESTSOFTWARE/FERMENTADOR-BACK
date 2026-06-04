import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.database import AsyncSessionLocal
from src.core.security import decode_token
from src.core.websocket.session_ws_manager import session_ws_manager
from src.services.auth.infrastructure.adapters.MySQL import AuthRepository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/session")
async def session_ws(websocket: WebSocket):
    """
    Canal de presencia de sesión (sesión única). Autenticado por cookie HttpOnly.
    Su única función es recibir `session:revoked` cuando el usuario inicia sesión
    en otro dispositivo, para expulsar este al instante.
    """
    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=4401)
        return
    try:
        payload   = decode_token(token)
        user_id   = int(payload["sub"])
        token_sid = payload.get("sid")
    except Exception:
        await websocket.close(code=4401)
        return

    # Solo la sesión activa actual puede mantener el canal abierto.
    active_sid = await AuthRepository(AsyncSessionLocal).get_active_session_id(user_id)
    if not token_sid or token_sid != active_sid:
        await websocket.close(code=4401)
        return

    await session_ws_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # keepalive; ignoramos el contenido
    except WebSocketDisconnect:
        await session_ws_manager.disconnect(user_id, websocket)
    except Exception as e:
        await session_ws_manager.disconnect(user_id, websocket)
        logger.error(f"[WS:Session] Error → user_id={user_id} | {e}")
