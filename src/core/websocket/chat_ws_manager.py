import asyncio
import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ChatWebSocketManager:
    """
    Manager de conexiones WebSocket del chat.

    Conexiones agrupadas por usuario:
        { user_id: [ws1, ws2, ...] }   ← un usuario puede tener varias pestañas/dispositivos

    Para emitir a una conversación, el caller resuelve los member_ids
    y llama a send_to_users(member_ids, event).
    """

    def __init__(self):
        self.connections: dict[int, list[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.connections.setdefault(user_id, []).append(websocket)
        logger.info(f"[WS:Chat] Conectado → user_id={user_id}")

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self.connections.get(user_id)
            if conns and websocket in conns:
                conns.remove(websocket)
                if not conns:
                    del self.connections[user_id]
        logger.info(f"[WS:Chat] Desconectado → user_id={user_id}")

    async def send_to_users(self, user_ids: list[int] | set[int], event: dict) -> None:
        """Empuja un evento (dict serializable) a todos los usuarios conectados de la lista."""
        async with self._lock:
            targets: list[tuple[int, WebSocket]] = [
                (uid, ws)
                for uid in set(user_ids)
                for ws in self.connections.get(uid, [])
            ]
        if not targets:
            return

        payload = json.dumps(event, default=str)
        results = await asyncio.gather(
            *[ws.send_text(payload) for _, ws in targets],
            return_exceptions=True,
        )

        dead = [(uid, ws) for (uid, ws), r in zip(targets, results) if isinstance(r, Exception)]
        if dead:
            async with self._lock:
                for uid, ws in dead:
                    conns = self.connections.get(uid)
                    if conns and ws in conns:
                        conns.remove(ws)
                        if not conns:
                            del self.connections[uid]


# ── Instancia global ──────────────────────────────────────────────────────────
chat_ws_manager = ChatWebSocketManager()
