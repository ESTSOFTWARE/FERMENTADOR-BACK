from datetime import datetime

from pydantic import BaseModel


class FermentadorResponse(BaseModel):
    id:             int
    serial:         str
    circuit_id:     int | None
    codigo:         str | None
    vendido:        bool
    estado:         str
    cliente_id:     int | None
    cliente_nombre: str | None
    alta_por:       str | None
    created_at:     datetime | None

    @classmethod
    def from_entity(cls, f) -> "FermentadorResponse":
        return cls(
            id             = f.id,
            serial         = f.serial,
            circuit_id     = f.circuit_id,
            codigo         = f.codigo,
            vendido        = f.vendido,
            estado         = f.estado,
            cliente_id     = f.cliente_id,
            cliente_nombre = f.cliente_nombre,
            alta_por       = f.alta_por,
            created_at     = f.created_at,
        )


class UpdateFermentadorRequest(BaseModel):
    vendido:    bool | None = None
    estado:     str | None = None
    cliente_id: int | None = None
