from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ── Config base: acepta snake_case interno, serializa en camelCase para el front ──
_camel = ConfigDict(populate_by_name=True)


# ── Sub-objetos ───────────────────────────────────────────────────────────────
class AttachmentDTO(BaseModel):
    model_config = _camel
    id:   int
    type: Literal["image", "video", "document", "file"]
    name: str
    url:  str
    size: int = 0


class MemberDTO(BaseModel):
    model_config = _camel
    id:     int
    name:   str
    role:   str
    avatar: str | None = None


class ReplyPreviewDTO(BaseModel):
    model_config = _camel
    id:          int
    content:     str | None = None
    sender_name: str             = Field(serialization_alias="senderName")
    attachment:  AttachmentDTO | None = None


# ── Respuestas ────────────────────────────────────────────────────────────────
class MessageResponse(BaseModel):
    model_config = _camel
    id:              int
    conversation_id: int             = Field(serialization_alias="conversationId")
    sender_id:       int             = Field(serialization_alias="senderId")
    sender_name:     str             = Field(serialization_alias="senderName")
    sender_role:     str             = Field(serialization_alias="senderRole")
    content:         str | None
    created_at:      datetime        = Field(serialization_alias="createdAt")
    read:            bool            = False
    status:          str             = "sent"
    deleted:         bool            = False
    edited:          bool            = False
    edited_at:       datetime | None = Field(default=None, serialization_alias="editedAt")
    pinned:          bool            = False
    priority:        str             = "normal"
    attachments:     list[AttachmentDTO] = []
    reply_to:        ReplyPreviewDTO | None = Field(default=None, serialization_alias="replyTo")
    reactions:       dict[str, list[int]]   = {}


class ConversationResponse(BaseModel):
    model_config = _camel
    id:           int
    type:         str
    name:         str | None = None
    description:  str | None = None
    avatar:       str | None = None
    members:      list[MemberDTO] = []
    last_message: MessageResponse | None = Field(default=None, serialization_alias="lastMessage")
    unread_count: int             = Field(default=0, serialization_alias="unreadCount")
    created_at:   datetime        = Field(serialization_alias="createdAt")
    created_by:   int             = Field(serialization_alias="createdBy")


class ContactDTO(BaseModel):
    model_config = _camel
    id:     int
    name:   str
    role:   str
    avatar: str | None = None


class UploadResponse(BaseModel):
    id:   int
    type: str
    name: str
    url:  str
    size: int


# ── Requests ──────────────────────────────────────────────────────────────────
class CreateConversationRequest(BaseModel):
    model_config = _camel
    type:        Literal["personal", "group"]
    member_ids:  list[int]   = Field(alias="memberIds")
    name:        str | None = None
    description: str | None = None


class UpdateConversationRequest(BaseModel):
    model_config = _camel
    name:        str | None = None
    description: str | None = None
    avatar:      str | None = None


class AttachmentInput(BaseModel):
    model_config = _camel
    id:   int
    type: Literal["image", "video", "document", "file"]
    name: str
    url:  str
    size: int = 0


class SendMessageRequest(BaseModel):
    model_config = _camel
    content:     str | None = None
    attachments: list[AttachmentInput] = []
    reply_to_id: int | None = Field(default=None, alias="replyToId")


class EditMessageRequest(BaseModel):
    content: str


class SetPriorityRequest(BaseModel):
    priority: Literal["normal", "important", "urgent"]


class ReactionRequest(BaseModel):
    emoji: str
