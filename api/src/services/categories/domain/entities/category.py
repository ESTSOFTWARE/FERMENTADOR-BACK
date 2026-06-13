from dataclasses import dataclass
from datetime import datetime


@dataclass
class Category:
    id:          int | None
    name:        str
    description: str | None
    created_at:  datetime | None = None
    updated_at:  datetime | None = None