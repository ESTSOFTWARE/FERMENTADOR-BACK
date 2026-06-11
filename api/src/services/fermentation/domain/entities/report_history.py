from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReportHistory:
    id:          int
    report_id:   int
    user_id:     int
    action:      str
    occurred_at: datetime | None = None
