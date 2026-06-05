import asyncio
import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class SupportWebSocketManager:
    """
    Conexiones WebSocket del chat de soporte, agrupadas por usuario.
    Para emitir a una conversación, el caller resuelve los destinatarios
    (el admin dueño + los agentes de soporte) y llama a send_to_users.
    """

    def __init__(self):
        self.connections: dict[int, list[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.connections.setdefault(user_id, []).append(websocket)
        logger.info(f"[WS:Support] Conectado → user_id={user_id}")

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self.connections.get(user_id)
            if conns and websocket in conns:
                conns.remove(websocket)
                if not conns:
                    del self.connections[user_id]

    async def send_to_users(self, user_ids: list[int] | set[int], event: dict) -> None:
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

    def online_user_ids(self) -> set[int]:
        return set(self.connections.keys())


# ── Instancia global ──────────────────────────────────────────────────────────
support_ws_manager = SupportWebSocketManager()
