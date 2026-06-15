import asyncio
import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class SessionWebSocketManager:
    """
    Conexiones WebSocket para expulsión instantánea de sesiones (sesión única).

    Conexiones agrupadas por usuario: { user_id: [ws, ...] }. Cuando un usuario
    inicia sesión en un dispositivo nuevo, se empuja `session:revoked` a todas
    las conexiones anteriores de ese usuario para sacarlas al instante.
    """

    def __init__(self):
        self.connections: dict[int, list[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            self.connections.setdefault(user_id, []).append(websocket)
        logger.info(f"[WS:Session] Conectado → user_id={user_id}")

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self.connections.get(user_id)
            if conns and websocket in conns:
                conns.remove(websocket)
                if not conns:
                    del self.connections[user_id]

    async def revoke(self, user_id: int) -> None:
        """Notifica a todas las conexiones actuales del usuario que su sesión fue reemplazada."""
        async with self._lock:
            conns = list(self.connections.get(user_id, []))
        if not conns:
            return
        payload = json.dumps({"type": "session:revoked"})
        await asyncio.gather(
            *[ws.send_text(payload) for ws in conns],
            return_exceptions=True,
        )
        logger.info(f"[WS:Session] Revocadas {len(conns)} conexión(es) previa(s) → user_id={user_id}")


# ── Instancia global ──────────────────────────────────────────────────────────
session_ws_manager = SessionWebSocketManager()
