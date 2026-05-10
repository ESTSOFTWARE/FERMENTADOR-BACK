from datetime import datetime

from pydantic import BaseModel


class SensorReadingResponse(BaseModel):
    id:          int
    circuit_id:  int
    sensor_type: str
    value:       float
    session_id:  int | None
    timestamp:   datetime | None

    @classmethod
    def from_entity(cls, reading) -> "SensorReadingResponse":
        return cls(
            id=reading.id,
            circuit_id=reading.circuit_id,
            sensor_type=reading.sensor_type,
            value=reading.value,
            session_id=reading.session_id,
            timestamp=reading.timestamp,
        )
