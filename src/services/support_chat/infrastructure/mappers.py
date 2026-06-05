from src.services.support_chat.domain.dto.support_chat_schema import (
    AttachmentDTO,
    SupportConversationResponse,
    SupportMessageResponse,
)
from src.services.support_chat.domain.entities.support_chat import (
    Attachment,
    SupportConversation,
    SupportMessage,
)


def attachment_dto(a: Attachment) -> AttachmentDTO:
    return AttachmentDTO(id=a.id, type=a.type, name=a.name, url=a.url, size=a.size)


def message_dto(m: SupportMessage) -> SupportMessageResponse:
    return SupportMessageResponse(
        id=m.id,
        conversation_id=m.conversation_id,
        sender_id=m.sender_id,
        sender_name=m.sender_name,
        sender_role=m.sender_role,
        content=m.content,
        created_at=m.created_at,
        read=m.read,
        attachments=[attachment_dto(a) for a in m.attachments],
    )


def conversation_dto(c: SupportConversation) -> SupportConversationResponse:
    return SupportConversationResponse(
        id=c.id,
        admin_id=c.admin_id,
        admin_name=c.admin_name,
        admin_email=c.admin_email,
        created_at=c.created_at,
        last_message=message_dto(c.last_message) if c.last_message else None,
        unread_count=c.unread_count,
    )
