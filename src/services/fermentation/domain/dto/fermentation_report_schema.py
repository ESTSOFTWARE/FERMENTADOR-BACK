from datetime import datetime

from pydantic import BaseModel


class FermentationReportResponse(BaseModel):
    id:                          int
    session_id:                  int
    initial_sugar:               float
    final_sugar:                 float | None
    ethanol_detected:            float | None
    theoretical_ethanol:         float | None
    efficiency:                  float | None
    alcohol_initial:             float | None
    alcohol_final:               float | None
    alcohol_deactivated_at:      datetime | None
    alcohol_last_reading:        float | None
    density_initial:             float | None
    density_final:               float | None
    density_deactivated_at:      datetime | None
    density_last_reading:        float | None
    conductivity_initial:        float | None
    conductivity_final:          float | None
    conductivity_deactivated_at: datetime | None
    conductivity_last_reading:   float | None
    ph_initial:                  float | None
    ph_final:                    float | None
    ph_deactivated_at:           datetime | None
    ph_last_reading:             float | None
    temperature_initial:         float | None
    temperature_final:           float | None
    temperature_deactivated_at:  datetime | None
    temperature_last_reading:    float | None
    turbidity_initial:           float | None
    turbidity_final:             float | None
    turbidity_deactivated_at:    datetime | None
    turbidity_last_reading:      float | None
    rpm_initial:                 float | None
    rpm_final:                   float | None
    rpm_deactivated_at:          datetime | None
    rpm_last_reading:            float | None
    notes:                       str | None
    generated_at:                datetime | None
