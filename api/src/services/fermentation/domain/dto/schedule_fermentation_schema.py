from datetime import datetime

from pydantic import BaseModel


class ScheduleFermentationRequest(BaseModel):
    circuit_id:      int
    group_id:        int | None = None
    scheduled_start: datetime
    scheduled_end:   datetime
    initial_sugar:   float
