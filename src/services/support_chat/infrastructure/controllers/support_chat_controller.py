from datetime import datetime, timezone

from fastapi import UploadFile

from src.core.cloudinary.upload_service import upload_chat_file
from src.core.database import AsyncSessionLocal
from src.services.support_chat.application.usecase.support_chat_use_cases import (
    GetMessagesUseCase,
    GetOrCreateMyConversationUseCase,
    ListConversationsUseCase,
    MarkReadUseCase,
    SendMessageUseCase,
)
from src.services.support_chat.domain.dto.support_chat_schema import (
    SendSupportMessageRequest,
    SupportConversationResponse,
    SupportMessageResponse,
    UploadResponse,
)
from src.services.support_chat.domain.entities.support_chat import Attachment
from src.services.support_chat.infrastructure import broadcaster
from src.services.support_chat.infrastructure.adapters.postgres import SupportChatRepository
from src.services.support_chat.infrastructure.mappers import conversation_dto, message_dto


def _repo() -> SupportChatRepository:
    return SupportChatRepository(AsyncSessionLocal)


async def get_my_conversation(user_id: int) -> SupportConversationResponse:
    repo = _repo()
    conv, created = await GetOrCreateMyConversationUseCase(repo).execute(user_id)
    dto = conversation_dto(conv)
    if created:
        await broadcaster.conversation_new(repo, dto)
    return dto


async def list_conversations() -> list[SupportConversationResponse]:
    convs = await ListConversationsUseCase(_repo()).execute()
    return [conversation_dto(c) for c in convs]


async def get_messages(
    conversation_id: int, user_id: int, role: str, cursor: int | None, limit: int,
) -> list[SupportMessageResponse]:
    msgs = await GetMessagesUseCase(_repo()).execute(conversation_id, user_id, role, cursor, limit)
    return [message_dto(m) for m in msgs]


async def send_message(
    conversation_id: int, body: SendSupportMessageRequest, user_id: int, role: str,
) -> SupportMessageResponse:
    repo = _repo()
    attachments = [
        Attachment(id=a.id, type=a.type, name=a.name, url=a.url, size=a.size)
        for a in body.attachments
    ]
    msg = await SendMessageUseCase(repo).execute(
        conversation_id=conversation_id,
        sender_id=user_id,
        role=role,
        content=body.content,
        attachments=attachments,
    )
    dto = message_dto(msg)
    await broadcaster.message_new(repo, dto)
    return dto


async def mark_read(conversation_id: int, user_id: int, role: str) -> dict:
    repo = _repo()
    await MarkReadUseCase(repo).execute(conversation_id, user_id, role)
    await broadcaster.read_updated(repo, conversation_id, role)
    return {"message": "ok"}


async def upload_file(file: UploadFile) -> UploadResponse:
    file_bytes = await file.read()
    result = await upload_chat_file(
        file_bytes=file_bytes,
        content_type=file.content_type or "",
        filename=file.filename or "archivo",
    )
    temp_id = int(datetime.now(timezone.utc).timestamp() * 1000)
    return UploadResponse(
        id=temp_id,
        type=result["type"],
        name=result["name"],
        url=result["url"],
        size=result["size"],
    )
