import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.rabbitmq.publisher import publisher

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/circuit/{circuit_id}/commands")
async def circuit_commands_ws(
    websocket: WebSocket,
    circuit_id: int,
):
    """
    Canal Front → Back → RabbitMQ → ESP32.
    El front manda el estado deseado de los dispositivos:
    {
        "motor": "encendido",
        "bomba": "apagado"
    }
    La API lo publica en RabbitMQ y el ESP32 lo recibe por MQTT.
    """
    await websocket.accept()
    logger.info(f"[WS:Commands] Cliente conectado → circuit_id={circuit_id}")

    try:
        while True:
            raw  = await websocket.receive_text()
            data = json.loads(raw)

            # Publicar el JSON tal cual en RabbitMQ
            # Routing key: commands.{circuit_id}.state
            # El ESP32 recibe por MQTT en: commands/{circuit_id}/state
            await publisher.publish_raw(
                exchange="amq.topic",
                routing_key=f"commands.{circuit_id}.state",
                payload=data,
            )

            # Confirmar al front
            await websocket.send_text(
                json.dumps({"status": "ok", "payload": data})
            )

            logger.debug(
                f"[WS:Commands] Comando publicado → circuit_id={circuit_id} | {data}"
            )

    except WebSocketDisconnect:
        logger.info(
            f"[WS:Commands] Cliente desconectado → circuit_id={circuit_id}"
        )

    except Exception as e:
        logger.error(
            f"[WS:Commands] Error → circuit_id={circuit_id} | {e}"
        )
        try:
            await websocket.close()
        except Exception:
            pass