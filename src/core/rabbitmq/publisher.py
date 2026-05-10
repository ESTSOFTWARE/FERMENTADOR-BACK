import json
import logging

import aio_pika

from src.core.exceptions import MessagePublishException
from src.core.rabbitmq.connection import rabbitmq
from src.core.websocket.schemas import CommandMessage

logger = logging.getLogger(__name__)


class Publisher:

    async def publish_command(self, command: CommandMessage):
        """
        Publica un comando al ESP32 vía MQTT usando amq.topic.
        Routing key: commands.{circuit_id}.{command_type}
        El ESP32 se suscribe al topic MQTT: commands/{circuit_id}/#
        """
        routing_key = f"commands.{command.circuit_id}.{command.type}"
        payload     = command.model_dump()

        await self.publish_raw(
            exchange="amq.topic",
            routing_key=routing_key,
            payload=payload,
        )

    async def publish_raw(
        self,
        exchange:    str,
        routing_key: str,
        payload:     dict,
    ):
        try:
            channel = await rabbitmq.get_channel()
            exch    = await channel.get_exchange(exchange)
            message = aio_pika.Message(
                body=json.dumps(payload).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await exch.publish(message, routing_key=routing_key)
            logger.debug(
                f"[Publisher] Publicado en {exchange} "
                f"→ routing_key={routing_key}"
            )

        except Exception as e:
            logger.error(f"[Publisher] Error publicando mensaje: {e}")
            raise MessagePublishException()


# Instancia global
publisher = Publisher()