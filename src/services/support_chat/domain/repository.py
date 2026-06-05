from abc import ABC, abstractmethod

from src.services.support_chat.domain.entities.support_chat import (
    Attachment,
    SupportConversation,
    SupportMessage,
)


class ISupportChatRepository(ABC):

    @abstractmethod
    async def get_or_create_for_admin(self, admin_id: int) -> tuple[SupportConversation, bool]:
        """Devuelve (conversación, creada). `creada=True` si se acaba de crear."""
        ...

    @abstractmethod
    async def get_conversation(self, conversation_id: int, viewer_role: str) -> SupportConversation | None: ...

    @abstractmethod
    async def list_conversations(self) -> list[SupportConversation]:
        """Cola para soporte: todas las conversaciones con lastMessage + unread (lado soporte)."""
        ...

    @abstractmethod
    async def is_admin_owner(self, conversation_id: int, admin_id: int) -> bool: ...

    @abstractmethod
    async def get_messages(
        self, conversation_id: int, viewer_role: str, cursor: int | None, limit: int,
    ) -> list[SupportMessage]: ...

    @abstractmethod
    async def create_message(
        self,
        conversation_id: int,
        sender_id:       int,
        sender_role:     str,
        content:         str | None,
        attachments:     list[Attachment],
    ) -> SupportMessage: ...

    @abstractmethod
    async def mark_read(self, conversation_id: int, viewer_role: str) -> None: ...

    @abstractmethod
    async def get_admin_id(self, conversation_id: int) -> int | None: ...

    @abstractmethod
    async def get_support_agent_ids(self) -> list[int]:
        """IDs de todos los usuarios con rol soporte (para broadcast a la cola)."""
        ...
