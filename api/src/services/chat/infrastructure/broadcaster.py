"""
Emite los eventos del chat por WebSocket a los miembros de cada conversación.
Se invoca desde los controllers después de persistir en BD (Fase 1).
"""
from src.core.rabbitmq.ws_events import to_users
from src.core.websocket.chat_ws_manager import chat_ws_manager
from src.services.chat.domain.dto.chat_schema import ConversationResponse, MessageResponse
from src.services.chat.domain.repository import IChatRepository


async def _member_ids(repo: IChatRepository, conversation_id: int) -> list[int]:
    members = await repo.get_members(conversation_id)
    return [m.id for m in members]


async def _emit(ids: list[int], payload: dict) -> None:
    """
    Entrega un evento del chat por dos vías durante la migración a Node:
    - In-process (chat_ws_manager): mientras el front siga en el /ws/chat de este back.
    - RabbitMQ (ws.events): para que el ws-service (Node) lo entregue vía gateway.
    `payload` es EXACTO lo que recibe el navegador. Cuando el WS viva 100% en
    Node, se elimina la vía in-process.
    """
    await chat_ws_manager.send_to_users(ids, payload)
    await to_users("chat", ids, payload)


async def message_new(repo: IChatRepository, msg: MessageResponse) -> None:
    ids = await _member_ids(repo, msg.conversation_id)
    await _emit(ids, {
        "type": "message:new",
        "message": msg.model_dump(by_alias=True, mode="json"),
    })


async def message_edited(repo: IChatRepository, msg: MessageResponse) -> None:
    ids = await _member_ids(repo, msg.conversation_id)
    await _emit(ids, {
        "type": "message:edited",
        "messageId": msg.id,
        "content": msg.content,
        "editedAt": msg.edited_at.isoformat() if msg.edited_at else None,
    })


async def message_deleted(repo: IChatRepository, conversation_id: int, message_id: int) -> None:
    ids = await _member_ids(repo, conversation_id)
    await _emit(ids, {
        "type": "message:deleted",
        "messageId": message_id,
    })


async def message_pinned(repo: IChatRepository, conversation_id: int, message_id: int, pinned: bool) -> None:
    ids = await _member_ids(repo, conversation_id)
    await _emit(ids, {
        "type": "message:pinned",
        "conversationId": conversation_id,
        "messageId": message_id if pinned else None,
    })


async def message_priority(repo: IChatRepository, conversation_id: int, message_id: int, priority: str) -> None:
    ids = await _member_ids(repo, conversation_id)
    await _emit(ids, {
        "type": "message:priority",
        "messageId": message_id,
        "priority": priority,
    })


async def reaction_updated(repo: IChatRepository, conversation_id: int, message_id: int, reactions: dict) -> None:
    ids = await _member_ids(repo, conversation_id)
    await _emit(ids, {
        "type": "reaction:updated",
        "messageId": message_id,
        "reactions": reactions,
    })


async def conversation_new(conv: ConversationResponse) -> None:
    member_ids = [m.id for m in conv.members]
    await _emit(member_ids, {
        "type": "conversation:new",
        "conversation": conv.model_dump(by_alias=True, mode="json"),
    })


async def conversation_updated(conv: ConversationResponse) -> None:
    member_ids = [m.id for m in conv.members]
    await _emit(member_ids, {
        "type": "conversation:updated",
        "conversation": conv.model_dump(by_alias=True, mode="json"),
    })


async def member_left(remaining_ids: list[int], conversation_id: int, user_id: int) -> None:
    await _emit(remaining_ids, {
        "type": "member:left",
        "conversationId": conversation_id,
        "userId": user_id,
    })
