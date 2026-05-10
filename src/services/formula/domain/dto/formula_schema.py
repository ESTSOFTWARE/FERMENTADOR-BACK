from datetime import datetime

from pydantic import BaseModel


class FormulaResponse(BaseModel):
    id:                int
    name:              str
    conversion_factor: float
    description:       str | None
    is_active:         bool
    updated_by:        int | None
    updated_at:        datetime | None
    created_at:        datetime | None

    @classmethod
    def from_entity(cls, formula) -> "FormulaResponse":
        return cls(
            id=formula.id,
            name=formula.name,
            conversion_factor=formula.conversion_factor,
            description=formula.description,
            is_active=formula.is_active,
            updated_by=formula.updated_by,
            updated_at=formula.updated_at,
            created_at=formula.created_at,
        )
