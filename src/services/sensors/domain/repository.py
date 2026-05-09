from abc import ABC, abstractmethod
from datetime import datetime
from src.services.sensors.domain.entities.sensor_reading import SensorReading


class ISensorRepository(ABC):

    @abstractmethod
    async def save_reading(
        self,
        circuit_id:  int,
        sensor_type: str,
        value:       float,
        session_id:  int | None = None,
    ) -> SensorReading:
        ...

    @abstractmethod
    async def get_history(
        self,
        circuit_id:  int,
        sensor_type: str,
        session_id:  int | None = None,
        from_dt:     datetime | None = None,
        to_dt:       datetime | None = None,
    ) -> list[SensorReading]:
        ...

    @abstractmethod
    async def get_latest_reading(
        self,
        circuit_id:  int,
        sensor_type: str,
    ) -> SensorReading | None:
        ...