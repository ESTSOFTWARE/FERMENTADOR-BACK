from fastapi import APIRouter, Depends, File, Query, UploadFile

from src.core.dependencies import require_any_role
from src.services.chat.domain.dto.chat_schema import (
    ContactDTO,
    ConversationResponse,
    CreateConversationRequest,
    EditMessageRequest,
    MemberDTO,
    MessageResponse,
    ReactionRequest,
    SendMessageRequest,
    SetPriorityRequest,
    UpdateConversationRequest,
    UploadResponse,
)
from src.services.chat.infrastructure.controllers.conversation_controller import (
    create_conversation,
    get_contacts,
    get_conversation_detail,
    get_conversations,
    get_members,
    leave_conversation,
    mark_read,
    update_conversation,
)
from src.services.chat.infrastructure.controllers.message_controller import (
    delete_message,
    edit_message,
    get_messages,
    pin_message,
    send_message,
    set_priority,
    toggle_reaction,
)
from src.services.chat.infrastructure.controllers.upload_controller import upload_file

router = APIRouter()


# ── Conversaciones ────────────────────────────────────────────────────────────
@router.get("/conversations", response_model=list[ConversationResponse], summary="Listar conversaciones del usuario")
async def list_conversations_route(current_user: dict = Depends(require_any_role)):
    return await get_conversations(current_user["user_id"])


@router.post("/conversations", response_model=ConversationResponse, status_code=201, summary="Crear conversación (cualquier rol)")
async def create_conversation_route(
    body: CreateConversationRequest,
    current_user: dict = Depends(require_any_role),
):
    return await create_conversation(body, current_user["user_id"])


@router.get("/contacts", response_model=list[ContactDTO], summary="Personas con las que el usuario puede chatear")
async def contacts_route(current_user: dict = Depends(require_any_role)):
    return await get_contacts(current_user["user_id"])


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse, summary="Detalle de conversación")
async def conversation_detail_route(
    conversation_id: int,
    current_user: dict = Depends(require_any_role),
):
    return await get_conversation_detail(conversation_id, current_user["user_id"])


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse, summary="Editar grupo (solo creador)")
async def update_conversation_route(
    conversation_id: int,
    body: UpdateConversationRequest,
    current_user: dict = Depends(require_any_role),
):
    return await update_conversation(conversation_id, body, current_user["user_id"])


@router.delete("/conversations/{conversation_id}/leave", summary="Abandonar conversación")
async def leave_conversation_route(
    conversation_id: int,
    current_user: dict = Depends(require_any_role),
):
    return await leave_conversation(conversation_id, current_user["user_id"])


@router.get("/conversations/{conversation_id}/members", response_model=list[MemberDTO], summary="Miembros de la conversación")
async def members_route(
    conversation_id: int,
    current_user: dict = Depends(require_any_role),
):
    return await get_members(conversation_id, current_user["user_id"])


@router.post("/conversations/{conversation_id}/read", summary="Marcar conversación como leída")
async def mark_read_route(
    conversation_id: int,
    current_user: dict = Depends(require_any_role),
):
    return await mark_read(conversation_id, current_user["user_id"])


# ── Mensajes ──────────────────────────────────────────────────────────────────
@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
    summary="Mensajes paginados (scroll infinito)",
)
async def messages_route(
    conversation_id: int,
    cursor: int | None = Query(None),
    limit:  int        = Query(30, ge=1, le=100),
    current_user: dict = Depends(require_any_role),
):
    return await get_messages(conversation_id, current_user["user_id"], cursor, limit)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=201,
    summary="Enviar mensaje",
)
async def send_message_route(
    conversation_id: int,
    body: SendMessageRequest,
    current_user: dict = Depends(require_any_role),
):
    return await send_message(conversation_id, body, current_user["user_id"])


@router.patch("/messages/{message_id}", response_model=MessageResponse, summary="Editar mensaje (autor + ≤20min)")
async def edit_message_route(
    message_id: int,
    body: EditMessageRequest,
    current_user: dict = Depends(require_any_role),
):
    return await edit_message(message_id, body, current_user["user_id"])


@router.delete("/messages/{message_id}", summary="Eliminar mensaje (soft, autor + ≤20min)")
async def delete_message_route(
    message_id: int,
    current_user: dict = Depends(require_any_role),
):
    return await delete_message(message_id, current_user["user_id"])


@router.post("/messages/{message_id}/pin", summary="Fijar/desfijar mensaje (solo creador del grupo)")
async def pin_message_route(
    message_id: int,
    current_user: dict = Depends(require_any_role),
):
    return await pin_message(message_id, current_user["user_id"])


@router.patch("/messages/{message_id}/priority", summary="Cambiar prioridad del mensaje")
async def set_priority_route(
    message_id: int,
    body: SetPriorityRequest,
    current_user: dict = Depends(require_any_role),
):
    return await set_priority(message_id, body, current_user["user_id"])


@router.post("/messages/{message_id}/reactions", summary="Reaccionar (toggle)")
async def reaction_route(
    message_id: int,
    body: ReactionRequest,
    current_user: dict = Depends(require_any_role),
):
    return await toggle_reaction(message_id, body, current_user["user_id"])


# ── Archivos ──────────────────────────────────────────────────────────────────
@router.post("/uploads", response_model=UploadResponse, summary="Subir archivo de chat")
async def upload_route(
    file: UploadFile = File(...),
    _: dict = Depends(require_any_role),
):
    return await upload_file(file)
