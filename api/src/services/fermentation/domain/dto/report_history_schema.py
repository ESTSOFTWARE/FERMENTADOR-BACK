from datetime import datetime

from pydantic import BaseModel


class ReportHistoryResponse(BaseModel):
    id:          int
    report_id:   int
    user_id:     int
    action:      str
    occurred_at: datetime | None
