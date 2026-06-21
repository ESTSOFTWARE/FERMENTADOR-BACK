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
class SupportMessage:
    id:              int
    conversation_id: int
    sender_id:       int
    sender_name:     str
    sender_role:     str          # admin | soporte
    content:         str | None
    created_at:      datetime
    read:            bool = False
    attachments:     list[Attachment] = field(default_factory=list)


@dataclass
class SupportConversation:
    id:           int
    admin_id:     int
    admin_name:   str
    admin_email:  str
    created_at:   datetime
    admin_image:  str | None = None
    last_message: SupportMessage | None = None
    unread_count: int = 0
