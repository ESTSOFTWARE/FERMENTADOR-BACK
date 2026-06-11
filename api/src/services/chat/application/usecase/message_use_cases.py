from datetime import datetime, timedelta

from src.core.exceptions import AppException, ForbiddenException
from src.services.chat.domain.entities.chat import Attachment, Message
from src.services.chat.domain.repository import IChatRepository

EDIT_WINDOW = timedelta(minutes=20)


def _not_found(detail: str = "Mensaje no encontrado") -> AppException:
    return AppException(status_code=404, detail=detail)


def _within_edit_window(created_at: datetime) -> bool:
    return (datetime.utcnow() - created_at) <= EDIT_WINDOW


class GetMessagesUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(
        self, conversation_id: int, user_id: int, cursor: int | None, limit: int,
    ) -> list[Message]:
        if not await self._repo.is_member(conversation_id, user_id):
            raise ForbiddenException("No perteneces a esta conversación")
        return await self._repo.get_messages(conversation_id, user_id, cursor, limit)


class SendMessageUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(
        self,
        conversation_id: int,
        sender_id:       int,
        content:         str | None,
        attachments:     list[Attachment],
        reply_to_id:     int | None,
    ) -> Message:
        if not await self._repo.is_member(conversation_id, sender_id):
            raise ForbiddenException("No perteneces a esta conversación")
        if not (content and content.strip()) and not attachments:
            raise AppException(status_code=400, detail="El mensaje no puede estar vacío")
        return await self._repo.create_message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            attachments=attachments,
            reply_to_id=reply_to_id,
        )


class EditMessageUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(self, message_id: int, user_id: int, content: str) -> Message:
        msg = await self._repo.get_message(message_id, user_id)
        if not msg:
            raise _not_found()
        if msg.sender_id != user_id:
            raise ForbiddenException("Solo el autor puede editar el mensaje")
        if msg.deleted:
            raise AppException(status_code=400, detail="No se puede editar un mensaje eliminado")
        if not _within_edit_window(msg.created_at):
            raise ForbiddenException("El tiempo para editar este mensaje (20 min) ya expiró")
        return await self._repo.update_message_content(message_id, content)


class DeleteMessageUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(self, message_id: int, user_id: int) -> int:
        msg = await self._repo.get_message(message_id, user_id)
        if not msg:
            raise _not_found()
        if msg.sender_id != user_id:
            raise ForbiddenException("Solo el autor puede eliminar el mensaje")
        if not _within_edit_window(msg.created_at):
            raise ForbiddenException("El tiempo para eliminar este mensaje (20 min) ya expiró")
        await self._repo.soft_delete_message(message_id)
        return msg.conversation_id


class PinMessageUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(self, message_id: int, user_id: int) -> tuple[int, bool]:
        msg = await self._repo.get_message(message_id, user_id)
        if not msg:
            raise _not_found()
        conv = await self._repo.get_conversation(msg.conversation_id, user_id)
        if not conv:
            raise _not_found("Conversación no encontrada")
        if conv.created_by != user_id:
            raise ForbiddenException("Solo el creador del grupo puede fijar mensajes")
        pinned = await self._repo.toggle_pin(message_id)
        return msg.conversation_id, pinned


class SetPriorityUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(self, message_id: int, user_id: int, priority: str) -> int:
        msg = await self._repo.get_message(message_id, user_id)
        if not msg:
            raise _not_found()
        conv = await self._repo.get_conversation(msg.conversation_id, user_id)
        if not conv:
            raise _not_found("Conversación no encontrada")
        if conv.created_by != user_id and msg.sender_id != user_id:
            raise ForbiddenException("No puedes cambiar la prioridad de este mensaje")
        await self._repo.set_priority(message_id, priority)
        return msg.conversation_id


class ToggleReactionUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(self, message_id: int, user_id: int, emoji: str) -> tuple[int, dict[str, list[int]]]:
        msg = await self._repo.get_message(message_id, user_id)
        if not msg:
            raise _not_found()
        if not await self._repo.is_member(msg.conversation_id, user_id):
            raise ForbiddenException("No perteneces a esta conversación")
        reactions = await self._repo.toggle_reaction(message_id, user_id, emoji)
        return msg.conversation_id, reactions
