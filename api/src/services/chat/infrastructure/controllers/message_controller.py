from src.core.database import AsyncSessionLocal
from src.services.chat.application.usecase.message_use_cases import (
    DeleteMessageUseCase,
    EditMessageUseCase,
    GetMessagesUseCase,
    PinMessageUseCase,
    SendMessageUseCase,
    SetPriorityUseCase,
    ToggleReactionUseCase,
)
from src.services.chat.domain.dto.chat_schema import (
    EditMessageRequest,
    MessageResponse,
    ReactionRequest,
    SendMessageRequest,
    SetPriorityRequest,
)
from src.services.chat.domain.entities.chat import Attachment
from src.services.chat.infrastructure import broadcaster
from src.services.chat.infrastructure.adapters.postgres import ChatRepository
from src.services.chat.infrastructure.mappers import message_dto


def _repo() -> ChatRepository:
    return ChatRepository(AsyncSessionLocal)


async def get_messages(
    conversation_id: int, user_id: int, cursor: int | None, limit: int,
) -> list[MessageResponse]:
    messages = await GetMessagesUseCase(_repo()).execute(conversation_id, user_id, cursor, limit)
    return [message_dto(m) for m in messages]


async def send_message(
    conversation_id: int, body: SendMessageRequest, user_id: int,
) -> MessageResponse:
    attachments = [
        Attachment(id=a.id, type=a.type, name=a.name, url=a.url, size=a.size)
        for a in body.attachments
    ]
    repo = _repo()
    msg  = await SendMessageUseCase(repo).execute(
        conversation_id=conversation_id,
        sender_id=user_id,
        content=body.content,
        attachments=attachments,
        reply_to_id=body.reply_to_id,
    )
    dto = message_dto(msg)
    await broadcaster.message_new(repo, dto)

    # Push a los demás miembros: "Ameth te envió un mensaje" (best-effort).
    try:
        import asyncio

        from src.core.fcm.fcm_service import send_push_to_user

        members = await repo.get_members(conversation_id)
        preview = dto.content.strip() if dto.content else "📎 Te envió un archivo"
        mentioned = set(body.mentions or [])
        tasks = []
        for m in members:
            if m.id == user_id:
                continue
            if m.id in mentioned:
                # Aviso especial de mención: "Ameth te mencionó".
                tasks.append(send_push_to_user(
                    user_id=m.id,
                    title=dto.sender_name,
                    body=f"Te mencionó: {preview}",
                    data={
                        "type": "chat_mention",
                        "conversation_id": conversation_id,
                        "message_id": dto.id,
                    },
                ))
            else:
                tasks.append(send_push_to_user(
                    user_id=m.id,
                    title=dto.sender_name,
                    body=preview,
                    data={"type": "chat_message", "conversation_id": conversation_id},
                ))
        await asyncio.gather(*tasks)
    except Exception:  # noqa: BLE001
        pass

    return dto


async def edit_message(message_id: int, body: EditMessageRequest, user_id: int) -> MessageResponse:
    repo = _repo()
    msg  = await EditMessageUseCase(repo).execute(message_id, user_id, body.content)
    dto  = message_dto(msg)
    await broadcaster.message_edited(repo, dto)
    return dto


async def delete_message(message_id: int, user_id: int) -> dict:
    repo            = _repo()
    conversation_id = await DeleteMessageUseCase(repo).execute(message_id, user_id)
    await broadcaster.message_deleted(repo, conversation_id, message_id)
    return {"message": "Mensaje eliminado"}


async def pin_message(message_id: int, user_id: int) -> dict:
    repo                    = _repo()
    conversation_id, pinned = await PinMessageUseCase(repo).execute(message_id, user_id)
    await broadcaster.message_pinned(repo, conversation_id, message_id, pinned)
    return {"messageId": message_id, "pinned": pinned}


async def set_priority(message_id: int, body: SetPriorityRequest, user_id: int) -> dict:
    repo            = _repo()
    conversation_id = await SetPriorityUseCase(repo).execute(message_id, user_id, body.priority)
    await broadcaster.message_priority(repo, conversation_id, message_id, body.priority)
    return {"messageId": message_id, "priority": body.priority}


async def toggle_reaction(message_id: int, body: ReactionRequest, user_id: int) -> dict:
    repo                       = _repo()
    conversation_id, reactions = await ToggleReactionUseCase(repo).execute(message_id, user_id, body.emoji)
    await broadcaster.reaction_updated(repo, conversation_id, message_id, reactions)
    return {"messageId": message_id, "reactions": reactions}
