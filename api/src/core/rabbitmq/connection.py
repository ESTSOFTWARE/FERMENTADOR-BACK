import asyncio
import logging

import aio_pika
from aio_pika import Channel, Connection

logger = logging.getLogger(__name__)


class RabbitMQConnection:

    def __init__(self):
        self._connection: Connection | None = None
        self._channel:    Channel | None    = None

    async def connect(self):
        from src.core.config import settings
        max_retries = 10
        delay       = 3

        for attempt in range(1, max_retries + 1):
            try:
                self._connection = await aio_pika.connect_robust(
                    settings.RABBITMQ_URL
                )
                self._channel = await self._connection.channel()
                await self._channel.set_qos(prefetch_count=10)
                logger.info("[RabbitMQ] Conexión establecida")
                return

            except Exception as e:
                logger.warning(
                    f"[RabbitMQ] Intento {attempt}/{max_retries} fallido: {e}"
                )
                if attempt < max_retries:
                    await asyncio.sleep(delay)

        raise RuntimeError("[RabbitMQ] No se pudo conectar después de varios intentos")

    async def get_channel(self) -> Channel:
        if self._channel is None or self._channel.is_closed:
            if self._connection and not self._connection.is_closed:
                self._channel = await self._connection.channel()
                await self._channel.set_qos(prefetch_count=10)
            else:
                await self.connect()
        return self._channel

    async def disconnect(self):
        try:
            if self._channel and not self._channel.is_closed:
                await self._channel.close()
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
            logger.info("[RabbitMQ] Conexión cerrada")
        except Exception as e:
            logger.error(f"[RabbitMQ] Error al cerrar conexión: {e}")


# Instancia global
rabbitmq = RabbitMQConnection()