from datetime import datetime

from pydantic import BaseModel


class AnnouncementResponse(BaseModel):
    id:           int
    label:        str
    version:      str
    date:         str
    title:        str
    description:  str
    created_at:   datetime | None = None
    is_pinned:    bool            = False
    pinned_until: datetime | None = None


class CreateAnnouncementRequest(BaseModel):
    label:       str
    version:     str
    date:        str | None = None  # si no se envía, el backend usa el mes actual
    title:       str
    description: str


class UpdateAnnouncementRequest(BaseModel):
    label:       str | None = None
    version:     str | None = None
    date:        str | None = None
    title:       str | None = None
    description: str | None = None


class PinAnnouncementRequest(BaseModel):
    duration_days: int | None = None  # None = pin indefinitely
