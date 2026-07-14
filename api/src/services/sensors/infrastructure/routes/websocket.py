import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.database import AsyncSessionLocal
from src.core.security import decode_token
from src.core.websocket.schemas import SensorDataMessage
from src.core.websocket.websocket_manager import ws_manager
from src.services.sensors.infrastructure.adapters.postgres import SensorRepository

logger = logging.getLogger(__name__)
router = APIRouter()

_ALL_SENSOR_TYPES = ["temperature", "alcohol", "conductivity", "turbidity", "ph", "rpm", "density"]


async def _send_snapshot(websocket: WebSocket, circuit_id: int) -> None:
    """Envía las últimas lecturas disponibles al cliente recién conectado."""
    sensor_repo = SensorRepository(AsyncSessionLocal)
    now = datetime.now(timezone.utc)
    for stype in _ALL_SENSOR_TYPES:
        try:
            reading = await sensor_repo.get_latest_reading(circuit_id, stype)
            if reading is None:
                continue
            msg = SensorDataMessage(
                circuit_id=circuit_id,
                sensor_type=stype,
                value=reading.value,
                session_id=reading.session_id,
                timestamp=reading.timestamp or now,
            )
            await websocket.send_text(msg.model_dump_json())
        except Exception:
            pass


@router.websocket("/ws/sensors/{circuit_id}")
async def sensors_ws(
    websocket: WebSocket,
    circuit_id: int,
):
    """
    Canal unidireccional Back → Front para datos de sensores en tiempo real.
    Al conectarse envía un snapshot inmediato con las últimas lecturas disponibles,
    luego sigue empujando actualizaciones conforme llegan del hardware.
    """
    user_id: int | None = None
    token = websocket.cookies.get("access_token") or websocket.query_params.get("token")
    if token:
        try:
            user_id = int(decode_token(token)["sub"])
        except Exception:
            user_id = None

    await ws_manager.connect_sensor(circuit_id, websocket, user_id)
    logger.info(f"[WS:Sensors] Cliente conectado → circuit_id={circuit_id} | user_id={user_id}")

    asyncio.create_task(_send_snapshot(websocket, circuit_id))

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        await ws_manager.disconnect_sensor(circuit_id, websocket)
        logger.info(f"[WS:Sensors] Cliente desconectado → circuit_id={circuit_id}")

    except Exception as e:
        await ws_manager.disconnect_sensor(circuit_id, websocket)
        logger.error(f"[WS:Sensors] Error → circuit_id={circuit_id} | {e}")
