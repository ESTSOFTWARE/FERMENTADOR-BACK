from datetime import datetime

from pydantic import BaseModel


class FermentationSessionResponse(BaseModel):
    id:              int
    circuit_id:      int
    user_id:         int
    group_id:        int | None = None
    formula_id:      int
    scheduled_start: datetime
    scheduled_end:   datetime
    actual_start:    datetime | None
    actual_end:      datetime | None
    status:          str
    interrupted_by:  int | None
    created_at:      datetime | None

    @classmethod
    def from_entity(cls, session) -> "FermentationSessionResponse":
        return cls(
            id              = session.id,
            circuit_id      = session.circuit_id,
            user_id         = session.user_id,
            group_id        = getattr(session, "group_id", None),
            formula_id      = session.formula_id,
            scheduled_start = session.scheduled_start,
            scheduled_end   = session.scheduled_end,
            actual_start    = session.actual_start,
            actual_end      = session.actual_end,
            status          = session.status,
            interrupted_by  = session.interrupted_by,
            created_at      = session.created_at,
        )
