import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.database import AsyncSessionLocal
from src.core.security import get_user_id_from_token
from src.core.websocket.chat_ws_manager import chat_ws_manager
from src.services.chat.infrastructure.adapters.MySQL import ChatRepository
from src.services.users.infrastructure.adapters.MySQL import UserRepository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket):
    """
    Canal bidireccional del chat, autenticado por cookie HttpOnly (access_token).

    Servidor → Cliente: message:new, message:edited, message:deleted, message:pinned,
                         message:priority, reaction:updated, conversation:new,
                         member:left, typing.
    Cliente → Servidor:  typing:start, typing:stop.
    """
    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=4401)
        return
    try:
        user_id = get_user_id_from_token(token)
    except Exception:
        await websocket.close(code=4401)
        return

    user = await UserRepository(AsyncSessionLocal).get_by_id(user_id)
    user_name = f"{user.name} {user.last_name}".strip() if user else "Usuario"
    repo = ChatRepository(AsyncSessionLocal)

    await chat_ws_manager.connect(user_id, websocket)

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
    except Exception as e:
        await chat_ws_manager.disconnect(user_id, websocket)
        logger.error(f"[WS:Chat] Error → user_id={user_id} | {e}")
