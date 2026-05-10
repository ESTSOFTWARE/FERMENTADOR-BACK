import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.websocket.websocket_manager import ws_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/notifications/{user_id}")
async def notifications_ws(
    websocket: WebSocket,
    user_id: int,
):
    """
    Canal unidireccional Back → Front para notificaciones en tiempo real.
    """
    await ws_manager.connect_notification(user_id, websocket)
    logger.info(f"[WS:Notifications] Cliente conectado → user_id={user_id}")

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        await ws_manager.disconnect_notification(user_id, websocket)
        logger.info(
            f"[WS:Notifications] Cliente desconectado → user_id={user_id}"
        )

    except Exception as e:
        await ws_manager.disconnect_notification(user_id, websocket)
        logger.error(
            f"[WS:Notifications] Error → user_id={user_id} | {e}"
        )