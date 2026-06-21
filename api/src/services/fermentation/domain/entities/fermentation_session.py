from dataclasses import dataclass
from datetime import datetime

from src.services.fermentation.domain.entities.fermentation_status import FermentationStatus


@dataclass
class FermentationSession:
    id:              int
    circuit_id:      int
    user_id:         int
    formula_id:      int
    scheduled_start: datetime
    scheduled_end:   datetime
    status:          FermentationStatus
    group_id:        int | None = None
    actual_start:    datetime | None = None
    actual_end:      datetime | None = None
    interrupted_by:  int | None = None
    created_at:      datetime | None = None
