"""
Emite los eventos del chat de soporte por WebSocket. Cada mensaje se envía
al admin dueño de la conversación + a todos los agentes de soporte.
"""
from collections.abc import Iterable

from src.core.rabbitmq.ws_events import to_users
from src.core.websocket.support_ws_manager import support_ws_manager
from src.services.support_chat.domain.dto.support_chat_schema import (
    SupportConversationResponse,
    SupportMessageResponse,
)
from src.services.support_chat.domain.repository import ISupportChatRepository


async def _recipients(repo: ISupportChatRepository, conversation_id: int) -> set[int]:
    admin_id = await repo.get_admin_id(conversation_id)
    agents   = await repo.get_support_agent_ids()
    ids = set(agents)
    if admin_id is not None:
        ids.add(admin_id)
    return ids


async def _emit(ids: Iterable[int], payload: dict) -> None:
    """
    Entrega un evento de soporte por dos vías durante la migración a Node:
    - In-process (support_ws_manager): mientras el front siga en /ws/support-chat de este back.
    - RabbitMQ (ws.events): para que el ws-service (Node) lo entregue vía gateway.
    `payload` es EXACTO lo que recibe el navegador.
    """
    await support_ws_manager.send_to_users(ids, payload)
    await to_users("support", list(ids), payload)


async def message_new(repo: ISupportChatRepository, msg: SupportMessageResponse) -> None:
    ids = await _recipients(repo, msg.conversation_id)
    await _emit(ids, {
        "type": "message:new",
        "message": msg.model_dump(by_alias=True, mode="json"),
    })


async def conversation_new(repo: ISupportChatRepository, conv: SupportConversationResponse) -> None:
    # Nueva conversación (un admin la abre por primera vez) → avisar a los agentes
    agents = await repo.get_support_agent_ids()
    await _emit(agents, {
        "type": "conversation:new",
        "conversation": conv.model_dump(by_alias=True, mode="json"),
    })


async def read_updated(repo: ISupportChatRepository, conversation_id: int, role: str) -> None:
    ids = await _recipients(repo, conversation_id)
    await _emit(ids, {
        "type": "read",
        "conversationId": conversation_id,
        "role": role,
    })
