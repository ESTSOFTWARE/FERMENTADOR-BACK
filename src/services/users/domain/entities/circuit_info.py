from dataclasses import dataclass
from datetime import datetime


@dataclass
class CircuitInfo:
    id:         int
    is_active:  bool
    created_at: datetime | None = None
