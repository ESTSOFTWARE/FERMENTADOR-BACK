from dataclasses import dataclass, field
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
    is_pinned:   bool            = field(default=False)
    pinned_until: datetime | None = field(default=None)
