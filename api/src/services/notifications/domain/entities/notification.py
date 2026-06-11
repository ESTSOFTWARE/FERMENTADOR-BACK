from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notification:
    id:         int
    user_id:    int
    message:    str
    type:       str
    status:     str
    session_id: int | None = None
    created_at: datetime | None = None
