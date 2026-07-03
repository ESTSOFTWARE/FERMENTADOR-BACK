from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Attachment:
    id:   int
    type: str          # image | video | document | file
    name: str
    url:  str
    size: int = 0


@dataclass
class Member:
    id:            int
    name:          str
    role:          str          # admin | profesor | estudiante
    avatar:        str | None = None


@dataclass
class ReplyPreview:
    id:          int
    content:     str | None
    sender_name: str
    attachment:  Attachment | None = None


@dataclass
class Message:
    id:              int
    conversation_id: int
    sender_id:       int
    sender_name:     str
    sender_role:     str
    content:         str | None
    created_at:      datetime
    read:            bool = False
    status:          str = "sent"   # sent | delivered | read (para MIS mensajes)
    deleted:         bool = False
    edited:          bool = False
    edited_at:       datetime | None = None
    pinned:          bool = False
    priority:        str = "normal"
    attachments:     list[Attachment] = field(default_factory=list)
    reply_to:        ReplyPreview | None = None
    reactions:       dict[str, list[int]] = field(default_factory=dict)


@dataclass
class Conversation:
    id:           int
    type:         str           # personal | group
    created_by:   int
    created_at:   datetime
    name:         str | None = None
    description:  str | None = None
    avatar:       str | None = None
    members:      list[Member] = field(default_factory=list)
    last_message: Message | None = None
    unread_count: int = 0
