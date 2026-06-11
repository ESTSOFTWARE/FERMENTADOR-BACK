from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id:         int
    user_id:    int
    message:    str
    type:       str
    status:     str
    session_id: int | None
    created_at: datetime | None

    @classmethod
    def from_entity(cls, n) -> "NotificationResponse":
        return cls(
            id=n.id,
            user_id=n.user_id,
            message=n.message,
            type=n.type,
            status=n.status,
            session_id=n.session_id,
            created_at=n.created_at,
        )
