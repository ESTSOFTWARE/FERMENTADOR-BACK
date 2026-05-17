from datetime import datetime

from pydantic import BaseModel


class AnnouncementResponse(BaseModel):
    id:          int
    label:       str
    version:     str
    date:        str
    title:       str
    description: str
    created_at:  datetime | None = None


class CreateAnnouncementRequest(BaseModel):
    label:       str
    version:     str
    date:        str | None = None  # si no se envía, el backend usa el mes actual
    title:       str
    description: str
