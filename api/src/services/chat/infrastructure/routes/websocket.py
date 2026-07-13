import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.database import AsyncSessionLocal
from src.core.security import decode_token
from src.core.websocket.chat_ws_manager import chat_ws_manager
from src.services.auth.infrastructure.adapters.postgres import AuthRepository
from src.services.chat.infrastructure.adapters.postgres import ChatRepository
from src.services.users.infrastructure.adapters.postgres import UserRepository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket, token: str | None = None):
    """
    Canal bidireccional del chat.
    Autenticación: cookie HttpOnly `access_token` (web) o query param `token` (móvil/API).

    Servidor → Cliente: message:new, message:edited, message:deleted, message:pinned,
                         message:priority, reaction:updated, conversation:new,
                         member:left, typing.
    Cliente → Servidor:  typing:start, typing:stop.
    """
    # Acepta cookie (web) o query param (móvil)
    token = token or websocket.cookies.get("access_token")
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

    # Sesión única: el token debe corresponder a la sesión activa del usuario.
    active_sid = await AuthRepository(AsyncSessionLocal).get_active_session_id(user_id)
    if not token_sid or token_sid != active_sid:
        await websocket.close(code=4401)
        return

    user = await UserRepository(AsyncSessionLocal).get_by_id(user_id)
    user_name = f"{user.name} {user.last_name}".strip() if user else "Usuario"
    repo = ChatRepository(AsyncSessionLocal)

    await chat_ws_manager.connect(user_id, websocket)

    # Presencia: notificar a contactos que este usuario entró, y enviarle quiénes ya están online.
    chatable_ids = await repo.get_chatable_user_ids(user_id)
    others = chatable_ids - {user_id}
    await chat_ws_manager.send_to_users(others, {"type": "user:online", "userId": user_id})
    online_now = list((chat_ws_manager.online_user_ids() & chatable_ids) - {user_id})
    await websocket.send_text(json.dumps({"type": "presence:init", "onlineUserIds": online_now}))

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
                if not await repo.is_member(conv_id, user_id):
                    continue
                members = await repo.get_members(conv_id)
                others  = [m.id for m in members if m.id != user_id]
                await chat_ws_manager.send_to_users(others, {
                    "type":           "typing",
                    "conversationId": conv_id,
                    "userId":         user_id,
                    "userName":       user_name,
                    "typing":         etype == "typing:start",
                })

    except WebSocketDisconnect:
        await chat_ws_manager.disconnect(user_id, websocket)
        if user_id not in chat_ws_manager.online_user_ids():
            await chat_ws_manager.send_to_users(others, {"type": "user:offline", "userId": user_id})
    except Exception as e:
        await chat_ws_manager.disconnect(user_id, websocket)
        if user_id not in chat_ws_manager.online_user_ids():
            await chat_ws_manager.send_to_users(others, {"type": "user:offline", "userId": user_id})
        logger.error(f"[WS:Chat] Error → user_id={user_id} | {e}")
