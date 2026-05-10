from datetime import datetime

from pydantic import BaseModel


class CircuitResponse(BaseModel):
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
    activated_at:           datetime | None
    created_at:             datetime | None
    active_sensors:         list[str]

    @classmethod
    def from_entity(cls, circuit) -> "CircuitResponse":
        return cls(
            id=circuit.id,
            activation_code=circuit.activation_code,
            is_active=circuit.is_active,
            motor_on=circuit.motor_on,
            pump_on=circuit.pump_on,
            sensor_alcohol_on=circuit.sensor_alcohol_on,
            sensor_density_on=circuit.sensor_density_on,
            sensor_conductivity_on=circuit.sensor_conductivity_on,
            sensor_ph_on=circuit.sensor_ph_on,
            sensor_temperature_on=circuit.sensor_temperature_on,
            sensor_turbidity_on=circuit.sensor_turbidity_on,
            sensor_rpm_on=circuit.sensor_rpm_on,
            activated_at=circuit.activated_at,
            created_at=circuit.created_at,
            active_sensors=circuit.get_active_sensors(),
        )
