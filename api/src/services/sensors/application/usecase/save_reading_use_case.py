from datetime import datetime, timezone

from src.core.rabbitmq.publisher import publisher
from src.core.rabbitmq.ws_events import to_room
from src.core.websocket.schemas import SensorDataMessage, SensorDeactivatedMessage
from src.core.websocket.websocket_manager import ws_manager
from src.services.sensors.domain.entities.sensor_reading import SensorReading
from src.services.sensors.domain.repository import ISensorRepository


class SaveReadingUseCase:

    def __init__(self, repository: ISensorRepository):
        self._repo = repository

    async def execute(
        self,
        circuit_id:  int,
        sensor_type: str,
        value:       float,
        session_id:  int | None = None,
    ) -> SensorReading:
        reading = await self._repo.save_reading(
            circuit_id=circuit_id,
            sensor_type=sensor_type,
            value=value,
            session_id=session_id,
        )

        msg = SensorDataMessage(
            circuit_id=circuit_id,
            sensor_type=sensor_type,
            value=value,
            session_id=session_id,
            timestamp=reading.timestamp or datetime.now(timezone.utc),
        )
        # In-process (transición): solo si hay clientes locales en el /ws de este back.
        if ws_manager.is_circuit_connected(circuit_id):
            await ws_manager.broadcast_sensor(circuit_id, msg)
        # RabbitMQ → ws-service (Node): siempre, a la sala del circuito.
        await to_room("sensors", f"circuit:{circuit_id}", msg.model_dump(mode="json"))

        return reading

    async def execute_deactivation(
        self,
        circuit_id:  int,
        sensor_type: str,
        session_id:  int,
        value:       float,
    ) -> None:
        now = datetime.now(timezone.utc)

        await publisher.publish_raw(
            exchange="sensor.events",
            routing_key="sensor.deactivated",
            payload={
                "session_id":     session_id,
                "sensor_type":    sensor_type,
                "last_reading":   value,
                "deactivated_at": now.isoformat(),
            },
        )

        msg = SensorDeactivatedMessage(
            circuit_id=circuit_id,
            sensor_type=sensor_type,
            session_id=session_id,
            last_reading=value,
            occurred_at=now,
        )
        if ws_manager.is_circuit_connected(circuit_id):
            await ws_manager.broadcast_sensor(circuit_id, msg)
        await to_room("sensors", f"circuit:{circuit_id}", msg.model_dump(mode="json"))