from dataclasses import dataclass
from datetime import datetime


@dataclass
class Announcement:
    id:          int
    label:       str
    version:     str
    date:        str
    title:       str
    description: str
    created_at:  datetime | None = None
