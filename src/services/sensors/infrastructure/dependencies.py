from src.core.database import AsyncSessionLocal
from src.services.sensors.infrastructure.adapters.MySQL import SensorRepository


def get_sensor_repository() -> SensorRepository:
    return SensorRepository(AsyncSessionLocal)