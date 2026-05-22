from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GroupMember:
    id:         int
    student_id: int
    name:       str
    last_name:  str
    email:      str
    joined_at:  datetime | None = None


@dataclass
class Group:
    id:           int
    name:         str
    professor_id: int
    code:         str
    created_at:   datetime | None = None
    members:      list[GroupMember] = field(default_factory=list)
