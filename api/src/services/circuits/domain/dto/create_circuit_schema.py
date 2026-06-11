from datetime import datetime

from pydantic import BaseModel


class CreateCircuitResponse(BaseModel):
    id:              int
    activation_code: str
    created_at:      datetime | None
