from dataclasses import dataclass
from datetime import datetime


@dataclass
class EfficiencyFormula:
    id:                int
    name:              str
    conversion_factor: float
    description:       str | None = None
    is_active:         bool = True
    updated_by:        int | None = None
    updated_at:        datetime | None = None
    created_at:        datetime | None = None
