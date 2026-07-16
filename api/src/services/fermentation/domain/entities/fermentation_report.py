from dataclasses import dataclass
from datetime import datetime


@dataclass
class FermentationReport:
    id:                          int
    session_id:                  int
    initial_sugar:               float
    final_sugar:                 float | None = None
    ethanol_detected:            float | None = None
    theoretical_ethanol:         float | None = None
    efficiency:                  float | None = None
    alcohol_initial:             float | None = None
    alcohol_final:               float | None = None
    alcohol_deactivated_at:      datetime | None = None
    alcohol_last_reading:        float | None = None
    density_initial:             float | None = None
    density_final:               float | None = None
    density_deactivated_at:      datetime | None = None
    density_last_reading:        float | None = None
    conductivity_initial:        float | None = None
    conductivity_final:          float | None = None
    conductivity_deactivated_at: datetime | None = None
    conductivity_last_reading:   float | None = None
    ph_initial:                  float | None = None
    ph_final:                    float | None = None
    ph_deactivated_at:           datetime | None = None
    ph_last_reading:             float | None = None
    temperature_initial:         float | None = None
    temperature_final:           float | None = None
    temperature_deactivated_at:  datetime | None = None
    temperature_last_reading:    float | None = None
    turbidity_initial:           float | None = None
    turbidity_final:             float | None = None
    turbidity_deactivated_at:    datetime | None = None
    turbidity_last_reading:      float | None = None
    rpm_initial:                 float | None = None
    rpm_final:                   float | None = None
    rpm_deactivated_at:          datetime | None = None
    rpm_last_reading:            float | None = None
    notes:                       str | None = None
    session_status:              str | None = None
    generated_at:                datetime | None = None
