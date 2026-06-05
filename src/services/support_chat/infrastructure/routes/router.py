from fastapi import APIRouter, Depends, File, Query, UploadFile

from src.core.dependencies import require_admin, require_admin_or_soporte, require_soporte
from src.services.support_chat.domain.dto.support_chat_schema import (
    SendSupportMessageRequest,
    SupportConversationResponse,
    SupportMessageResponse,
    UploadResponse,
)
from src.services.support_chat.infrastructure.controllers.support_chat_controller import (
    get_messages,
    get_my_conversation,
    list_conversations,
    mark_read,
    send_message,
    upload_file,
)

router = APIRouter()


@router.get("/me", response_model=SupportConversationResponse, summary="(Admin) Mi conversación con soporte")
async def my_conversation_route(current_user: dict = Depends(require_admin)):
    return await get_my_conversation(current_user["user_id"])


@router.get("/conversations", response_model=list[SupportConversationResponse], summary="(Soporte) Cola de conversaciones")
async def conversations_route(_: dict = Depends(require_soporte)):
    return await list_conversations()


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[SupportMessageResponse],
    summary="Mensajes paginados",
)
async def messages_route(
    conversation_id: int,
    cursor: int | None = Query(None),
    limit:  int        = Query(30, ge=1, le=100),
    current_user: dict = Depends(require_admin_or_soporte),
):
    return await get_messages(conversation_id, current_user["user_id"], current_user["role"], cursor, limit)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=SupportMessageResponse,
    status_code=201,
    summary="Enviar mensaje (admin o soporte)",
)
async def send_message_route(
    conversation_id: int,
    body: SendSupportMessageRequest,
    current_user: dict = Depends(require_admin_or_soporte),
):
    return await send_message(conversation_id, body, current_user["user_id"], current_user["role"])


@router.post("/conversations/{conversation_id}/read", summary="Marcar conversación como leída")
async def mark_read_route(
    conversation_id: int,
    current_user: dict = Depends(require_admin_or_soporte),
):
    return await mark_read(conversation_id, current_user["user_id"], current_user["role"])


@router.post("/uploads", response_model=UploadResponse, summary="Subir adjunto de soporte")
async def upload_route(
    file: UploadFile = File(...),
    _: dict = Depends(require_admin_or_soporte),
):
    return await upload_file(file)
