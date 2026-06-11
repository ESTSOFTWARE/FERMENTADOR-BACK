from pydantic import BaseModel


class UpdateFormulaRequest(BaseModel):
    name:              str | None = None
    conversion_factor: float | None = None
    description:       str | None = None
