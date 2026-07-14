from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

# ── Tipos de mensajes ─────────────────────────────────────────────────────────
SensorMessageType    = Literal["sensor_data", "sensor_deactivated"]
NotificationMsgType  = Literal[
    "fermentation_complete",
    "fermentation_interrupted",
    "high_temperature",
    "sensor_failure",
    "new_announcement",
    "member_added",
    "member_removed",
    "user_registered",
    "experiment_complete",
    "recommendation",
    "anomaly",
    "general",
]
CommandMessageType   = Literal[
    "sensor_on",
    "sensor_off",
    "motor_on",
    "motor_off",
    "pump_on",
    "pump_off",
    "start_fermentation",
    "stop_fermentation"
]


# ── Mensajes de sensores (Back → Front) ───────────────────────────────────────
class SensorDataMessage(BaseModel):
    """
    Mensaje que el back envía al front cuando llega una lectura de sensor.
    Canal: WS /ws/sensors/{circuit_id}
    """
    type:        SensorMessageType = "sensor_data"
    sensor_type: str
    value:       float
    circuit_id:  int
    session_id:  int | None = None
    timestamp:   datetime
    active:      bool = True


class SensorDeactivatedMessage(BaseModel):
    """
    Mensaje que el back envía al front cuando un sensor se desactiva.
    Canal: WS /ws/sensors/{circuit_id}
    """
    type:         Literal["sensor_deactivated"] = "sensor_deactivated"
    sensor_type:  str
    circuit_id:   int
    session_id:   int | None = None
    last_reading: float | None = None
    occurred_at:  datetime


# ── Mensajes de notificaciones (Back → Front) ─────────────────────────────────
class NotificationMessage(BaseModel):
    """
    Mensaje que el back envía al front para alertas.
    Canal: WS /ws/notifications/{user_id}
    """
    type:          NotificationMsgType
    notification_id: int
    message:       str
    session_id:    int | None = None
    occurred_at:   datetime


# ── Mensajes de comandos (Front → Back → RabbitMQ → ESP32) ───────────────────
class CommandMessage(BaseModel):
    """
    Mensaje que el front envía al WS para controlar el circuito.
    Canal: WS /ws/circuit/{circuit_id}/commands
    El back solo lo valida y lo publica en RabbitMQ sin procesarlo.
    """
    type:        CommandMessageType
    target:      str                    # sensor_type, 'motor', 'pump' o 'all'
    circuit_id:  int


# ── Mensaje de error WS ───────────────────────────────────────────────────────
class WSErrorMessage(BaseModel):
    """Mensaje de error estándar para cualquier canal WS."""
    type:    Literal["error"] = "error"
    detail:  str
    occurred_at: datetime = datetime.now()


# ── Mensaje genérico entrante desde ESP32 vía RabbitMQ ────────────────────────
class ESP32SensorPayload(BaseModel):
    """
    Payload que las ESP32 publican en RabbitMQ [sensor.data].
    El consumer.py deserializa este modelo al recibir cada mensaje.
    """
    circuit_id:  int
    sensor_type: str
    value:       float
    active:      bool = True
    session_id:  int | None = None
    timestamp:   datetime