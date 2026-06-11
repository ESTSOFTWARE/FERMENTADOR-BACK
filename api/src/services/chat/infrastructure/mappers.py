from src.services.chat.domain.dto.chat_schema import (
    AttachmentDTO,
    ConversationResponse,
    MemberDTO,
    MessageResponse,
    ReplyPreviewDTO,
)
from src.services.chat.domain.entities.chat import (
    Attachment,
    Conversation,
    Member,
    Message,
    ReplyPreview,
)


def attachment_dto(a: Attachment) -> AttachmentDTO:
    return AttachmentDTO(id=a.id, type=a.type, name=a.name, url=a.url, size=a.size)


def member_dto(m: Member) -> MemberDTO:
    return MemberDTO(id=m.id, name=m.name, role=m.role, avatar=m.avatar)


def reply_dto(r: ReplyPreview) -> ReplyPreviewDTO:
    return ReplyPreviewDTO(
        id=r.id,
        content=r.content,
        sender_name=r.sender_name,
        attachment=attachment_dto(r.attachment) if r.attachment else None,
    )


def message_dto(m: Message) -> MessageResponse:
    return MessageResponse(
        id=m.id,
        conversation_id=m.conversation_id,
        sender_id=m.sender_id,
        sender_name=m.sender_name,
        sender_role=m.sender_role,
        content=m.content,
        created_at=m.created_at,
        read=m.read,
        deleted=m.deleted,
        edited=m.edited,
        edited_at=m.edited_at,
        pinned=m.pinned,
        priority=m.priority,
        attachments=[attachment_dto(a) for a in m.attachments],
        reply_to=reply_dto(m.reply_to) if m.reply_to else None,
        reactions=m.reactions,
    )


def conversation_dto(c: Conversation) -> ConversationResponse:
    return ConversationResponse(
        id=c.id,
        type=c.type,
        name=c.name,
        description=c.description,
        avatar=c.avatar,
        members=[member_dto(m) for m in c.members],
        last_message=message_dto(c.last_message) if c.last_message else None,
        unread_count=c.unread_count,
        created_at=c.created_at,
        created_by=c.created_by,
    )
