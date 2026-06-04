from src.core.database import AsyncSessionLocal
from src.services.sensors.domain.dto.sensor_reading_schema import SensorReadingResponse
from src.services.sensors.infrastructure.adapters.postgres import SensorRepository


async def get_latest(circuit_id: int, sensor_type: str) -> SensorReadingResponse | None:
    repo = SensorRepository(AsyncSessionLocal)
    reading = await repo.get_latest_reading(circuit_id, sensor_type)
    return SensorReadingResponse.from_entity(reading) if reading else None
