from src.core.exceptions import AppException, ForbiddenException
from src.services.support_chat.domain.entities.support_chat import (
    Attachment,
    SupportConversation,
    SupportMessage,
)
from src.services.support_chat.domain.repository import ISupportChatRepository


def _not_found(detail: str = "Conversación no encontrada") -> AppException:
    return AppException(status_code=404, detail=detail)


async def _assert_access(repo: ISupportChatRepository, conversation_id: int, user_id: int, role: str) -> None:
    """admin solo accede a su propia conversación; soporte accede a cualquiera."""
    if role == "soporte":
        if await repo.get_admin_id(conversation_id) is None:
            raise _not_found()
        return
    # admin
    if not await repo.is_admin_owner(conversation_id, user_id):
        raise ForbiddenException("No tienes acceso a esta conversación")


class GetOrCreateMyConversationUseCase:
    """Admin: obtiene (o crea) su conversación con soporte."""
    def __init__(self, repo: ISupportChatRepository):
        self._repo = repo

    async def execute(self, admin_id: int) -> tuple[SupportConversation, bool]:
        return await self._repo.get_or_create_for_admin(admin_id)


class ListConversationsUseCase:
    """Soporte: cola de todas las conversaciones."""
    def __init__(self, repo: ISupportChatRepository):
        self._repo = repo

    async def execute(self) -> list[SupportConversation]:
        return await self._repo.list_conversations()


class GetMessagesUseCase:
    def __init__(self, repo: ISupportChatRepository):
        self._repo = repo

    async def execute(
        self, conversation_id: int, user_id: int, role: str, cursor: int | None, limit: int,
    ) -> list[SupportMessage]:
        await _assert_access(self._repo, conversation_id, user_id, role)
        return await self._repo.get_messages(conversation_id, role, cursor, limit)


class SendMessageUseCase:
    def __init__(self, repo: ISupportChatRepository):
        self._repo = repo

    async def execute(
        self,
        conversation_id: int,
        sender_id:       int,
        role:            str,
        content:         str | None,
        attachments:     list[Attachment],
    ) -> SupportMessage:
        await _assert_access(self._repo, conversation_id, sender_id, role)
        if not (content and content.strip()) and not attachments:
            raise AppException(status_code=400, detail="El mensaje no puede estar vacío")
        return await self._repo.create_message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            sender_role=role,
            content=content,
            attachments=attachments,
        )


class MarkReadUseCase:
    def __init__(self, repo: ISupportChatRepository):
        self._repo = repo

    async def execute(self, conversation_id: int, user_id: int, role: str) -> None:
        await _assert_access(self._repo, conversation_id, user_id, role)
        await self._repo.mark_read(conversation_id, role)
