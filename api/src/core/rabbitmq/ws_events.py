"""
Publicación de eventos WebSocket al servicio Node (ws-service) vía RabbitMQ.

El back ya NO empuja los sockets en proceso: publica un "sobre" en el exchange
`ws.events` y el ws-service (Node) lo consume y lo entrega a los clientes
conectados. El contrato del sobre es:

    {
      "channel": "session",            # canal (= routing key ws.{channel})
      "target":  {"users": [5]},       # a quién entregar (users) o {"room": "..."}
      "data":    {"type": "...", ...}  # EXACTO lo que recibe el navegador
    }

La entrega por WebSocket es best-effort: si RabbitMQ no está disponible, se
registra el error pero NO se propaga (no debe romper el flujo de negocio).
"""
import asyncio
import logging

from src.core.rabbitmq.publisher import publisher

logger = logging.getLogger(__name__)

WS_EXCHANGE = "ws.events"

# La entrega por WS es best-effort: si el broker tarda/está caído, fallamos
# rápido para no bloquear el flujo de negocio (login, envío de mensaje, etc.).
_PUBLISH_TIMEOUT = 2.0


async def publish_ws_event(channel: str, target: dict, data: dict) -> None:
    """Publica un evento para que el ws-service lo entregue. Best-effort."""
    envelope = {"channel": channel, "target": target, "data": data}
    try:
        await asyncio.wait_for(
            publisher.publish_raw(
                exchange="ws.events",
                routing_key=f"ws.{channel}",
                payload=envelope,
            ),
            timeout=_PUBLISH_TIMEOUT,
        )
    except (Exception, asyncio.TimeoutError) as e:  # noqa: BLE001 — best-effort
        logger.warning(f"[ws_events] No se pudo publicar {channel}: {e}")


async def to_users(channel: str, user_ids: list[int], data: dict) -> None:
    """Atajo: entregar a una lista de usuarios."""
    await publish_ws_event(channel, {"users": user_ids}, data)


async def to_room(channel: str, room: str, data: dict) -> None:
    """Atajo: entregar a todos los sockets de una sala (ej. sensores)."""
    await publish_ws_event(channel, {"room": room}, data)
