from dataclasses import dataclass
from datetime import datetime


@dataclass
class Circuit:
    id:                     int
    activation_code:        str
    is_active:              bool
    motor_on:               bool
    pump_on:                bool
    sensor_alcohol_on:      bool
    sensor_density_on:      bool
    sensor_conductivity_on: bool
    sensor_ph_on:           bool
    sensor_temperature_on:  bool
    sensor_turbidity_on:    bool
    sensor_rpm_on:          bool
    activated_at:           datetime | None = None
    created_at:             datetime | None = None

    def get_active_sensors(self) -> list[str]:
        sensors = []
        if self.sensor_alcohol_on:
            sensors.append("alcohol")
        if self.sensor_density_on:
            sensors.append("density")
        if self.sensor_conductivity_on:
            sensors.append("conductivity")
        if self.sensor_ph_on:
            sensors.append("ph")
        if self.sensor_temperature_on:
            sensors.append("temperature")
        if self.sensor_turbidity_on:
            sensors.append("turbidity")
        if self.sensor_rpm_on:
            sensors.append("rpm")
        return sensors
