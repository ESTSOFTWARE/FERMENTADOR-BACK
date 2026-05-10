import asyncio
import json
import logging
from datetime import datetime

from fastapi import WebSocket
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manager central de conexiones WebSocket activas.

    Maneja dos canales independientes:
    - sensor_connections:       { circuit_id: [ws1, ws2, ...] }  → datos de sensores
    - notification_connections: { user_id:    [ws1, ws2, ...] }  → notificaciones
    """

    def __init__(self):
        # circuit_id → lista de websockets conectados
        self.sensor_connections: dict[int, list[WebSocket]] = {}
        # user_id → lista de websockets conectados
        self.notification_connections: dict[int, list[WebSocket]] = {}
        # Lock para evitar condiciones de carrera al modificar los dicts
        self._lock = asyncio.Lock()


    # ── Sensores ──────────────────────────────────────────────────────────────
    async def connect_sensor(self, circuit_id: int, websocket: WebSocket) -> None:
        """Registra una conexión WS al canal de sensores de un circuito."""
        await websocket.accept()
        async with self._lock:
            if circuit_id not in self.sensor_connections:
                self.sensor_connections[circuit_id] = []
            self.sensor_connections[circuit_id].append(websocket)
        logger.info(f"[WS] Sensor conectado → circuit_id={circuit_id}")

    async def disconnect_sensor(self, circuit_id: int, websocket: WebSocket) -> None:
        """Elimina una conexión WS del canal de sensores."""
        async with self._lock:
            if circuit_id in self.sensor_connections:
                self.sensor_connections[circuit_id].remove(websocket)
                if not self.sensor_connections[circuit_id]:
                    del self.sensor_connections[circuit_id]
        logger.info(f"[WS] Sensor desconectado → circuit_id={circuit_id}")

    async def broadcast_sensor(self, circuit_id: int, message: BaseModel) -> None:
        """
        Envía un mensaje a todos los clientes conectados al canal
        de sensores de un circuito específico.
        """
        connections = self.sensor_connections.get(circuit_id, [])
        if not connections:
            return

        payload = message.model_dump_json()
        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_text(payload)
            except Exception:
                disconnected.append(websocket)
                logger.warning(
                    f"[WS] Conexión rota en sensor broadcast → circuit_id={circuit_id}"
                )

        # Limpiar conexiones muertas
        if disconnected:
            async with self._lock:
                for ws in disconnected:
                    if ws in self.sensor_connections.get(circuit_id, []):
                        self.sensor_connections[circuit_id].remove(ws)


    # ── Notificaciones ────────────────────────────────────────────────────────
    async def connect_notification(self, user_id: int, websocket: WebSocket) -> None:
        """Registra una conexión WS al canal de notificaciones de un usuario."""
        await websocket.accept()
        async with self._lock:
            if user_id not in self.notification_connections:
                self.notification_connections[user_id] = []
            self.notification_connections[user_id].append(websocket)
        logger.info(f"[WS] Notificación conectada → user_id={user_id}")

    async def disconnect_notification(self, user_id: int, websocket: WebSocket) -> None:
        """Elimina una conexión WS del canal de notificaciones."""
        async with self._lock:
            if user_id in self.notification_connections:
                self.notification_connections[user_id].remove(websocket)
                if not self.notification_connections[user_id]:
                    del self.notification_connections[user_id]
        logger.info(f"[WS] Notificación desconectada → user_id={user_id}")

    async def broadcast_notification(self, user_id: int, message: BaseModel) -> None:
        """
        Envía una notificación a todos los clientes conectados
        al canal de notificaciones de un usuario específico.
        """
        connections = self.notification_connections.get(user_id, [])
        if not connections:
            return

        payload = message.model_dump_json()
        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_text(payload)
            except Exception:
                disconnected.append(websocket)
                logger.warning(
                    f"[WS] Conexión rota en notification broadcast → user_id={user_id}"
                )

        # Limpiar conexiones muertas
        if disconnected:
            async with self._lock:
                for ws in disconnected:
                    if ws in self.notification_connections.get(user_id, []):
                        self.notification_connections[user_id].remove(ws)


    # ── Helpers ───────────────────────────────────────────────────────────────
    def get_sensor_connection_count(self, circuit_id: int) -> int:
        """Retorna cuántos clientes están escuchando un circuito."""
        return len(self.sensor_connections.get(circuit_id, []))

    def get_notification_connection_count(self, user_id: int) -> int:
        """Retorna cuántos clientes están escuchando notificaciones de un usuario."""
        return len(self.notification_connections.get(user_id, []))

    def is_circuit_connected(self, circuit_id: int) -> bool:
        """Verifica si hay al menos un cliente escuchando el circuito."""
        return bool(self.sensor_connections.get(circuit_id))

    def is_user_connected(self, user_id: int) -> bool:
        """Verifica si hay al menos un cliente escuchando notificaciones del usuario."""
        return bool(self.notification_connections.get(user_id))


# ── Instancia global ──────────────────────────────────────────────────────────
ws_manager = WebSocketManager()