from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GroupMember:
    id:             int
    student_id:     int
    name:           str
    last_name:      str
    email:          str
    avatar:         str | None = None
    joined_at:      datetime | None = None
    oauth_provider: str = 'email'
    dial_code:      str | None = None
    phone_number:   str | None = None
    description:    str | None = None


@dataclass
class Group:
    id:           int
    name:         str
    subject:      str
    professor_id: int
    code:         str
    professor_name:  str | None = None
    professor_email: str | None = None
    professor_avatar: str | None = None
    cover_image:  str | None = None
    created_at:   datetime | None = None
    members:      list[GroupMember] = field(default_factory=list)
