import asyncio
import json
import logging
from datetime import datetime
from aio_pika import IncomingMessage
from src.core.rabbitmq.connection import rabbitmq

logger = logging.getLogger(__name__)


class FermentationEventConsumer:

    def __init__(self):
        self._fermentation_repo = None
        self._task              = None

    def set_dependencies(self, fermentation_repository):
        self._fermentation_repo = fermentation_repository

    async def start(self):
        self._task = asyncio.create_task(self._consume())
        logger.info("[FermentationConsumer] Tarea iniciada")

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("[FermentationConsumer] Tarea detenida")

    async def _consume(self):
        try:
            channel = await rabbitmq.get_channel()
            queue   = await channel.declare_queue(
                "sensor.deactivated.queue",
                durable=True,
                passive=True,
            )
            logger.info("[FermentationConsumer] Escuchando sensor.deactivated.queue...")
            async with queue.iterator() as messages:
                async for message in messages:
                    asyncio.create_task(self._handle(message))

        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"[FermentationConsumer] Error: {e}")

    async def _handle(self, message: IncomingMessage):
        async with message.process():
            try:
                data           = json.loads(message.body.decode())
                session_id     = data["session_id"]
                sensor_type    = data["sensor_type"]
                last_reading   = data["last_reading"]
                deactivated_at = datetime.fromisoformat(data["deactivated_at"])

                await self._fermentation_repo.update_sensor_deactivation(
                    session_id=session_id,
                    sensor_type=sensor_type,
                    last_reading=last_reading,
                    deactivated_at=deactivated_at,
                )
                logger.debug(
                    f"[FermentationConsumer] sensor.deactivated procesado: "
                    f"session={session_id} sensor={sensor_type}"
                )

            except Exception as e:
                logger.error(f"[FermentationConsumer] Error procesando evento: {e}")


fermentation_event_consumer = FermentationEventConsumer()
