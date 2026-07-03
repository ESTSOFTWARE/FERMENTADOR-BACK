from abc import ABC, abstractmethod

from src.services.chat.domain.entities.chat import (
    Attachment,
    Conversation,
    Member,
    Message,
)


class IChatRepository(ABC):

    # ── Jerarquía ─────────────────────────────────────────────────────────────
    @abstractmethod
    async def get_chatable_user_ids(self, user_id: int) -> set[int]: ...

    @abstractmethod
    async def get_contacts(self, user_id: int) -> list[Member]: ...

    # ── Conversaciones ────────────────────────────────────────────────────────
    @abstractmethod
    async def get_conversations_for_user(self, user_id: int) -> list[Conversation]: ...

    @abstractmethod
    async def get_conversation(self, conversation_id: int, viewer_id: int) -> Conversation | None: ...

    @abstractmethod
    async def create_conversation(
        self,
        type:        str,
        created_by:  int,
        member_ids:  list[int],
        name:        str | None,
        description: str | None,
    ) -> Conversation: ...

    @abstractmethod
    async def find_personal_conversation(self, user_a: int, user_b: int) -> Conversation | None: ...

    @abstractmethod
    async def update_conversation(
        self,
        conversation_id: int,
        name:            str | None,
        description:     str | None,
        avatar:          str | None,
    ) -> Conversation: ...

    @abstractmethod
    async def remove_member(self, conversation_id: int, user_id: int) -> None: ...

    @abstractmethod
    async def get_members(self, conversation_id: int) -> list[Member]: ...

    @abstractmethod
    async def is_member(self, conversation_id: int, user_id: int) -> bool: ...

    # ── Mensajes ──────────────────────────────────────────────────────────────
    @abstractmethod
    async def get_messages(
        self,
        conversation_id: int,
        viewer_id:       int,
        cursor:          int | None,
        limit:           int,
    ) -> list[Message]: ...

    @abstractmethod
    async def get_message(self, message_id: int, viewer_id: int | None = None) -> Message | None: ...

    @abstractmethod
    async def create_message(
        self,
        conversation_id: int,
        sender_id:       int,
        content:         str | None,
        attachments:     list[Attachment],
        reply_to_id:     int | None,
    ) -> Message: ...

    @abstractmethod
    async def update_message_content(self, message_id: int, content: str) -> Message: ...

    @abstractmethod
    async def soft_delete_message(self, message_id: int) -> None: ...

    @abstractmethod
    async def toggle_pin(self, message_id: int) -> bool: ...

    @abstractmethod
    async def set_priority(self, message_id: int, priority: str) -> None: ...

    @abstractmethod
    async def toggle_reaction(self, message_id: int, user_id: int, emoji: str) -> dict[str, list[int]]: ...

    @abstractmethod
    async def mark_read(self, conversation_id: int, user_id: int) -> None: ...

    @abstractmethod
    async def mark_delivered(self, conversation_id: int, user_id: int) -> None: ...
