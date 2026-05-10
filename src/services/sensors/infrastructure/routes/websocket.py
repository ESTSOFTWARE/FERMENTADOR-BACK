import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.websocket.websocket_manager import ws_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/sensors/{circuit_id}")
async def sensors_ws(
    websocket: WebSocket,
    circuit_id: int,
):
    """
    Canal unidireccional Back → Front para datos de sensores en tiempo real.
    El front se conecta y recibe SensorDataMessage / SensorDeactivatedMessage.
    """
    await ws_manager.connect_sensor(circuit_id, websocket)
    logger.info(f"[WS:Sensors] Cliente conectado → circuit_id={circuit_id}")

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        await ws_manager.disconnect_sensor(circuit_id, websocket)
        logger.info(
            f"[WS:Sensors] Cliente desconectado → circuit_id={circuit_id}"
        )

    except Exception as e:
        await ws_manager.disconnect_sensor(circuit_id, websocket)
        logger.error(
            f"[WS:Sensors] Error → circuit_id={circuit_id} | {e}"
        )