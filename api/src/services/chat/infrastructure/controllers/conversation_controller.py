from datetime import datetime

from src.core.database import AsyncSessionLocal
from src.core.exceptions import ForbiddenException, NotFoundException
from src.services.chat.application.usecase.conversation_use_cases import (
    CreateConversationUseCase,
    GetContactsUseCase,
    GetConversationDetailUseCase,
    GetConversationsUseCase,
    GetMembersUseCase,
    LeaveConversationUseCase,
    MarkReadUseCase,
    UpdateConversationUseCase,
)
from src.services.chat.domain.dto.chat_schema import (
    ContactDTO,
    ConversationResponse,
    CreateConversationRequest,
    MemberDTO,
    UpdateConversationRequest,
)
from src.services.chat.infrastructure import broadcaster
from src.services.chat.infrastructure.adapters.postgres import ChatRepository
from src.services.chat.infrastructure.mappers import conversation_dto, member_dto


def _repo() -> ChatRepository:
    return ChatRepository(AsyncSessionLocal)


async def get_conversations(user_id: int) -> list[ConversationResponse]:
    convs = await GetConversationsUseCase(_repo()).execute(user_id)
    return [conversation_dto(c) for c in convs]


async def get_contacts(user_id: int) -> list[ContactDTO]:
    contacts = await GetContactsUseCase(_repo()).execute(user_id)
    return [ContactDTO(id=c.id, name=c.name, role=c.role, avatar=c.avatar) for c in contacts]


async def create_conversation(body: CreateConversationRequest, user_id: int) -> ConversationResponse:
    conv = await CreateConversationUseCase(_repo()).execute(
        creator_id=user_id,
        type=body.type,
        member_ids=body.member_ids,
        name=body.name,
        description=body.description,
    )
    dto = conversation_dto(conv)
    await broadcaster.conversation_new(dto)
    return dto


async def get_conversation_detail(conversation_id: int, user_id: int) -> ConversationResponse:
    conv = await GetConversationDetailUseCase(_repo()).execute(conversation_id, user_id)
    return conversation_dto(conv)


async def add_members(
    conversation_id: int, user_ids: list[int], requester_id: int,
) -> ConversationResponse:
    repo = _repo()
    # Solo el creador del grupo puede agregar miembros.
    conv = await repo.get_conversation(conversation_id, requester_id)
    if not conv:
        raise NotFoundException("Conversación no encontrada")
    if conv.created_by != requester_id:
        raise ForbiddenException(
            "Solo el creador del grupo puede agregar miembros"
        )
    for uid in user_ids:
        await repo.add_member(conversation_id, uid)

    conv = await GetConversationDetailUseCase(repo).execute(conversation_id, requester_id)
    dto = conversation_dto(conv)
    # El nuevo miembro obtiene la conversación; los demás refrescan sus miembros.
    await broadcaster.conversation_new(dto)
    await broadcaster.conversation_updated(dto)
    return dto


async def update_conversation(
    conversation_id: int, body: UpdateConversationRequest, user_id: int,
) -> ConversationResponse:
    conv = await UpdateConversationUseCase(_repo()).execute(
        conversation_id=conversation_id,
        user_id=user_id,
        name=body.name,
        description=body.description,
        avatar=body.avatar,
    )
    dto = conversation_dto(conv)
    await broadcaster.conversation_updated(dto)
    return dto


async def leave_conversation(conversation_id: int, user_id: int) -> dict:
    remaining = await LeaveConversationUseCase(_repo()).execute(conversation_id, user_id)
    await broadcaster.member_left(remaining, conversation_id, user_id)
    return {"message": "Has abandonado la conversación"}


async def get_members(conversation_id: int, user_id: int) -> list[MemberDTO]:
    members = await GetMembersUseCase(_repo()).execute(conversation_id, user_id)
    return [member_dto(m) for m in members]


async def mark_read(conversation_id: int, user_id: int) -> dict:
    repo = _repo()
    await MarkReadUseCase(repo).execute(conversation_id, user_id)
    # Avisar al remitente para pintar las flechas azules (leído).
    await broadcaster.conversation_read(
        repo, conversation_id, user_id, datetime.utcnow().isoformat()
    )
    return {"message": "ok"}


async def mark_delivered(conversation_id: int, user_id: int) -> dict:
    repo = _repo()
    await repo.mark_delivered(conversation_id, user_id)
    # Avisar al remitente para pintar la doble flecha gris (entregado).
    await broadcaster.conversation_delivered(
        repo, conversation_id, user_id, datetime.utcnow().isoformat()
    )
    return {"message": "ok"}
