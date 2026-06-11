import logging

import aio_pika

from src.core.rabbitmq.connection import rabbitmq

logger = logging.getLogger(__name__)


class ExchangeManager:

    async def setup(self):
        channel = await rabbitmq.get_channel()

        # ── Exchange sensor.data (AMQP → back) ───────────────────────────────
        sensor_exchange = await channel.declare_exchange(
            "sensor.data",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        sensor_queue = await channel.declare_queue(
            "sensor.data.queue",
            durable=True,
            arguments={
                "x-message-ttl": 60_000,
                "x-max-length":  10_000,
            },
        )
        await sensor_queue.bind(sensor_exchange, routing_key="#")
        logger.info("[Exchanges] sensor.data configurado")

        # ── Exchange amq.topic (MQTT → back) ─────────────────────────────────
        # RabbitMQ enruta los mensajes MQTT a este exchange automáticamente.
        # El topic MQTT sensors/1/temperature llega como routing key sensors.1.temperature
        mqtt_exchange = await channel.declare_exchange(
            "amq.topic",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
            passive=True,  # ya existe en RabbitMQ, solo lo referenciamos
        )
        mqtt_queue = await channel.declare_queue(
            "mqtt.sensor.data.queue",
            durable=True,
            arguments={
                "x-message-ttl": 60_000,
                "x-max-length":  10_000,
            },
        )
        await mqtt_queue.bind(mqtt_exchange, routing_key="sensors.#")
        logger.info("[Exchanges] amq.topic (MQTT) configurado")

        # ── Exchange circuit.commands (back → ESP32 vía MQTT) ────────────────
        # El back publica aquí, RabbitMQ lo convierte a MQTT para el ESP32
        commands_exchange = await channel.declare_exchange(
            "amq.topic",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
            passive=True,  # mismo exchange amq.topic, distinto routing key
        )
        commands_queue = await channel.declare_queue(
            "circuit.commands.queue",
            durable=True,
            arguments={
                "x-message-ttl": 30_000,
                "x-max-length":  1_000,
            },
        )
        await commands_queue.bind(commands_exchange, routing_key="commands.#")
        logger.info("[Exchanges] circuit.commands configurado")

        # ── Exchange sensor.events (eventos internos entre servicios) ─────────
        sensor_events_exchange = await channel.declare_exchange(
            "sensor.events",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        sensor_deactivated_queue = await channel.declare_queue(
            "sensor.deactivated.queue",
            durable=True,
            arguments={
                "x-message-ttl": 300_000,
                "x-max-length":  5_000,
            },
        )
        await sensor_deactivated_queue.bind(
            sensor_events_exchange, routing_key="sensor.deactivated"
        )
        logger.info("[Exchanges] sensor.events configurado")

        # ── Exchange ws.events (back → servicio WebSocket en Node) ───────────
        # El back publica el "sobre" {channel, target, data} con routing key
        # ws.{channel}; el ws-service (Node) consume y entrega por WebSocket.
        # No declaramos cola aquí: cada instancia de Node crea su cola exclusiva.
        await channel.declare_exchange(
            "ws.events",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        logger.info("[Exchanges] ws.events configurado")


# Instancia global
exchange_manager = ExchangeManager()