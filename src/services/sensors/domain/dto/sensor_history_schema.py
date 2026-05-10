from pydantic import BaseModel

from src.services.sensors.domain.dto.sensor_reading_schema import SensorReadingResponse


class SensorHistoryResponse(BaseModel):
    circuit_id:  int
    sensor_type: str
    readings:    list[SensorReadingResponse]
