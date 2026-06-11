from dataclasses import dataclass
from datetime import datetime


@dataclass
class SensorReading:
    id:          int
    circuit_id:  int
    sensor_type: str
    value:       float
    session_id:  int | None = None
    timestamp:   datetime | None = None
