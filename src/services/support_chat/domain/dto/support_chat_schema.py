from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

_camel = ConfigDict(populate_by_name=True)


# ── Sub-objetos ───────────────────────────────────────────────────────────────
class AttachmentDTO(BaseModel):
    model_config = _camel
    id:   int
    type: Literal["image", "video", "document", "file"]
    name: str
    url:  str
    size: int = 0


# ── Respuestas ────────────────────────────────────────────────────────────────
class SupportMessageResponse(BaseModel):
    model_config = _camel
    id:              int
    conversation_id: int             = Field(serialization_alias="conversationId")
    sender_id:       int             = Field(serialization_alias="senderId")
    sender_name:     str             = Field(serialization_alias="senderName")
    sender_role:     str             = Field(serialization_alias="senderRole")
    content:         str | None
    created_at:      datetime        = Field(serialization_alias="createdAt")
    read:            bool            = False
    attachments:     list[AttachmentDTO] = []


class SupportConversationResponse(BaseModel):
    model_config = _camel
    id:           int
    admin_id:     int             = Field(serialization_alias="adminId")
    admin_name:   str             = Field(serialization_alias="adminName")
    admin_email:  str             = Field(serialization_alias="adminEmail")
    created_at:   datetime        = Field(serialization_alias="createdAt")
    last_message: SupportMessageResponse | None = Field(default=None, serialization_alias="lastMessage")
    unread_count: int             = Field(default=0, serialization_alias="unreadCount")


class UploadResponse(BaseModel):
    id:   int
    type: str
    name: str
    url:  str
    size: int


# ── Requests ──────────────────────────────────────────────────────────────────
class AttachmentInput(BaseModel):
    model_config = _camel
    id:   int
    type: Literal["image", "video", "document", "file"]
    name: str
    url:  str
    size: int = 0


class SendSupportMessageRequest(BaseModel):
    model_config = _camel
    content:     str | None = None
    attachments: list[AttachmentInput] = []
