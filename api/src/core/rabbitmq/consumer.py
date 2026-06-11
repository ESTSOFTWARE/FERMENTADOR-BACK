import asyncio
import json
import logging

from aio_pika import IncomingMessage

from src.core.config import settings
from src.core.rabbitmq.connection import rabbitmq

logger = logging.getLogger(__name__)


class SensorConsumer:

    def __init__(self):
        self._save_reading_uc      = None
        self._send_notification_uc = None
        self._fermentation_repo    = None
        self._task_amqp            = None
        self._task_mqtt            = None

    def set_dependencies(
        self,
        save_reading_use_case,
        send_notification_use_case,
        fermentation_repository,
    ):
        self._save_reading_uc      = save_reading_use_case
        self._send_notification_uc = send_notification_use_case
        self._fermentation_repo    = fermentation_repository

    async def start(self):
        self._task_amqp = asyncio.create_task(self._consume_amqp())
        self._task_mqtt = asyncio.create_task(self._consume_mqtt())
        logger.info("[Consumer] Tareas iniciadas (AMQP + MQTT)")

    async def stop(self):
        for task in [self._task_amqp, self._task_mqtt]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        logger.info("[Consumer] Tareas detenidas")

    # ── Consumers ─────────────────────────────────────────────────────────────

    async def _consume_amqp(self):
        try:
            channel = await rabbitmq.get_channel()
            queue   = await channel.declare_queue(
                "sensor.data.queue",
                durable=True,
                passive=True,
            )
            logger.info("[Consumer:AMQP] Escuchando sensor.data.queue...")
            async with queue.iterator() as messages:
                async for message in messages:
                    asyncio.create_task(self._handle_amqp_message(message))

        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"[Consumer:AMQP] Error: {e}")

    async def _consume_mqtt(self):
        try:
            channel = await rabbitmq.get_channel()
            queue   = await channel.declare_queue(
                "mqtt.sensor.data.queue",
                durable=True,
                passive=True,
            )
            logger.info("[Consumer:MQTT] Escuchando mqtt.sensor.data.queue...")
            async with queue.iterator() as messages:
                async for message in messages:
                    asyncio.create_task(self._handle_mqtt_message(message))

        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"[Consumer:MQTT] Error: {e}")

    # ── Handlers ──────────────────────────────────────────────────────────────

    async def _handle_amqp_message(self, message: IncomingMessage):
        async with message.process():
            try:
                data   = json.loads(message.body.decode())
                active = data.get("active", True)

                if active:
                    await self._handle_active_reading(data)
                else:
                    await self._handle_deactivated_sensor(data)

            except Exception as e:
                logger.error(f"[Consumer:AMQP] Error procesando mensaje: {e}")

    async def _handle_mqtt_message(self, message: IncomingMessage):
        async with message.process():
            try:
                routing_key = message.routing_key or ""
                parts       = routing_key.split(".")

                if len(parts) < 3 or parts[0] != "sensors":
                    logger.warning(
                        f"[Consumer:MQTT] Routing key inválida: {routing_key}"
                    )
                    return

                circuit_id  = int(parts[1])
                sensor_type = parts[2]
                body        = json.loads(message.body.decode())

                data = {
                    "circuit_id":  circuit_id,
                    "sensor_type": sensor_type,
                    "value":       float(body.get("value", 0)),
                    "session_id":  body.get("session_id"),
                    "active":      body.get("active", True),
                }

                logger.debug(
                    f"[Consumer:MQTT] {sensor_type} "
                    f"circuit={circuit_id} value={data['value']}"
                )

                if data["active"]:
                    await self._handle_active_reading(data)
                else:
                    await self._handle_deactivated_sensor(data)

            except Exception as e:
                logger.error(f"[Consumer:MQTT] Error procesando mensaje: {e}")

    # ── Lógica compartida ─────────────────────────────────────────────────────

    async def _handle_active_reading(self, data: dict):
        circuit_id  = data["circuit_id"]
        sensor_type = data["sensor_type"]
        value       = data["value"]
        session_id  = data.get("session_id")

        await self._save_reading_uc.execute(
            circuit_id=circuit_id,
            sensor_type=sensor_type,
            value=value,
            session_id=session_id,
        )

        if sensor_type == "temperature":
            await self._trigger_temperature_alert(
                circuit_id=circuit_id,
                value=value,
                session_id=session_id,
            )

    async def _handle_deactivated_sensor(self, data: dict):
        circuit_id  = data["circuit_id"]
        sensor_type = data["sensor_type"]
        value       = data.get("value", 0.0)
        session_id  = data.get("session_id")

        if session_id:
            await self._save_reading_uc.execute_deactivation(
                circuit_id=circuit_id,
                sensor_type=sensor_type,
                session_id=session_id,
                value=value,
            )

    async def _trigger_temperature_alert(
        self,
        circuit_id: int,
        value:      float,
        session_id: int | None,
    ):
        if value < settings.TEMPERATURE_ALERT_THRESHOLD:
            return

        try:
            user_id = await self._fermentation_repo.get_user_id_by_circuit(circuit_id)
            if not user_id:
                return

            await self._send_notification_uc.execute(
                user_id=user_id,
                message=(
                    f"⚠️ Temperatura crítica: {value}°C "
                    f"(umbral: {settings.TEMPERATURE_ALERT_THRESHOLD}°C)"
                ),
                notification_type="high_temperature",
                session_id=session_id,
            )

        except Exception as e:
            logger.error(f"[Consumer] Error enviando alerta de temperatura: {e}")


# Instancia global
consumer = SensorConsumer()
