from dataclasses import dataclass
from datetime import datetime


@dataclass
class Fermentador:
    id:         int
    serial:     str
    circuit_id: int | None
    vendido:    bool
    estado:     str
    created_by: int | None = None
    cliente_id: int | None = None
    created_at: datetime | None = None
    # Campos derivados (joins) para la respuesta
    codigo:         str | None = None  # activation_code del circuito
    alta_por:       str | None = None  # nombre de created_by
    cliente_nombre: str | None = None  # nombre del cliente asignado
