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

La entrega por WebSocket es best-effort y NO bloqueante: se publica en segundo
plano (fire-and-forget). Si RabbitMQ no está disponible (ej. dev local sin
broker), se registra el error pero el flujo de negocio (login, envío de mensaje,
lecturas de sensor) sigue inmediato — sin esperas.
"""
import asyncio
import logging

from src.core.rabbitmq.publisher import publisher

logger = logging.getLogger(__name__)

WS_EXCHANGE = "ws.events"

# Tope por si el broker tarda; la publicación va en background, así que esto solo
# acota cuánto vive la tarea de fondo, no bloquea la request.
_PUBLISH_TIMEOUT = 2.0


async def _do_publish(channel: str, envelope: dict) -> None:
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


def publish_ws_event(channel: str, target: dict, data: dict) -> None:
    """
    Programa la publicación de un evento para que el ws-service lo entregue.
    Fire-and-forget: no espera al broker, nunca bloquea la request.
    """
    envelope = {"channel": channel, "target": target, "data": data}
    try:
        asyncio.get_running_loop().create_task(_do_publish(channel, envelope))
    except RuntimeError:
        # Sin loop corriendo (ej. script suelto): publica de forma síncrona.
        asyncio.run(_do_publish(channel, envelope))


async def to_users(channel: str, user_ids: list[int], data: dict) -> None:
    """Atajo: entregar a una lista de usuarios (no bloqueante)."""
    publish_ws_event(channel, {"users": user_ids}, data)


async def to_room(channel: str, room: str, data: dict) -> None:
    """Atajo: entregar a todos los sockets de una sala, ej. sensores (no bloqueante)."""
    publish_ws_event(channel, {"room": room}, data)
