import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.database import AsyncSessionLocal
from src.core.security import decode_token
from src.core.websocket.support_ws_manager import support_ws_manager
from src.services.auth.infrastructure.adapters.postgres import AuthRepository
from src.services.support_chat.infrastructure.adapters.postgres import SupportChatRepository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/support-chat")
async def support_chat_ws(websocket: WebSocket):
    """
    Canal en tiempo real del chat de soporte (admin ↔ soporte).
    Autenticado por cookie HttpOnly (access_token + sid de sesión única).

    Servidor → Cliente: message:new, conversation:new, read, typing.
    Cliente → Servidor:  typing:start, typing:stop.
    """
    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=4401)
        return
    try:
        payload   = decode_token(token)
        user_id   = int(payload["sub"])
        role      = payload.get("role")
        token_sid = payload.get("sid")
    except Exception:
        await websocket.close(code=4401)
        return

    # Solo admin y soporte usan este canal
    if role not in ("admin", "soporte"):
        await websocket.close(code=4403)
        return

    # Sesión única: el token debe corresponder a la sesión activa
    active_sid = await AuthRepository(AsyncSessionLocal).get_active_session_id(user_id)
    if not token_sid or token_sid != active_sid:
        await websocket.close(code=4401)
        return

    repo = SupportChatRepository(AsyncSessionLocal)
    await support_ws_manager.connect(user_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            etype   = data.get("type")
            conv_id = data.get("conversationId")

            if etype in ("typing:start", "typing:stop") and conv_id:
                admin_id = await repo.get_admin_id(conv_id)
                if admin_id is None:
                    continue
                # admin solo puede "escribir" en su propia conversación
                if role == "admin" and admin_id != user_id:
                    continue
                agents   = await repo.get_support_agent_ids()
                others   = ({admin_id, *agents}) - {user_id}
                await support_ws_manager.send_to_users(others, {
                    "type":           "typing",
                    "conversationId": conv_id,
                    "userId":         user_id,
                    "role":           role,
                    "typing":         etype == "typing:start",
                })

    except WebSocketDisconnect:
        await support_ws_manager.disconnect(user_id, websocket)
    except Exception as e:
        await support_ws_manager.disconnect(user_id, websocket)
        logger.error(f"[WS:Support] Error → user_id={user_id} | {e}")
