from datetime import datetime

from pydantic import BaseModel


class ScheduleFermentationRequest(BaseModel):
    circuit_id:      int
    scheduled_start: datetime
    scheduled_end:   datetime
    initial_sugar:   float
