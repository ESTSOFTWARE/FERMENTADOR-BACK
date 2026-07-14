from datetime import datetime, timezone

from pydantic import BaseModel, field_validator, model_validator


class ScheduleFermentationRequest(BaseModel):
    circuit_id:      int
    group_id:        int | None = None
    scheduled_start: datetime
    scheduled_end:   datetime
    initial_sugar:   float

    @field_validator("scheduled_start", "scheduled_end", mode="after")
    @classmethod
    def _to_naive_utc(cls, v: datetime) -> datetime:
        # El front manda fechas con zona (ISO con 'Z'), pero las columnas son
        # TIMESTAMP WITHOUT TIME ZONE → convertimos a UTC naive para asyncpg.
        if v.tzinfo is not None:
            v = v.astimezone(timezone.utc).replace(tzinfo=None)
        return v

    @model_validator(mode="after")
    def _validate_range(self):
        # Validación cruzada: la fecha de fin debe ser posterior a la de inicio.
        if self.scheduled_end <= self.scheduled_start:
            raise ValueError(
                "La fecha de fin debe ser posterior a la de inicio",
            )
        if self.initial_sugar <= 0:
            raise ValueError("El azúcar inicial debe ser mayor a 0")
        return self
