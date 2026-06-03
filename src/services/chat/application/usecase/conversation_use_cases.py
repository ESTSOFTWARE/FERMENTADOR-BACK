from src.core.exceptions import AppException, ForbiddenException
from src.services.chat.domain.entities.chat import Conversation, Member
from src.services.chat.domain.repository import IChatRepository


def _not_found(detail: str = "Conversación no encontrada") -> AppException:
    return AppException(status_code=404, detail=detail)


class GetConversationsUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(self, user_id: int) -> list[Conversation]:
        return await self._repo.get_conversations_for_user(user_id)


class GetContactsUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(self, user_id: int) -> list[Member]:
        return await self._repo.get_contacts(user_id)


class GetConversationDetailUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(self, conversation_id: int, user_id: int) -> Conversation:
        if not await self._repo.is_member(conversation_id, user_id):
            raise ForbiddenException("No perteneces a esta conversación")
        conv = await self._repo.get_conversation(conversation_id, user_id)
        if not conv:
            raise _not_found()
        return conv


class GetMembersUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(self, conversation_id: int, user_id: int) -> list[Member]:
        if not await self._repo.is_member(conversation_id, user_id):
            raise ForbiddenException("No perteneces a esta conversación")
        return await self._repo.get_members(conversation_id)


class CreateConversationUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(
        self,
        creator_id:  int,
        type:        str,
        member_ids:  list[int],
        name:        str | None,
        description: str | None,
    ) -> Conversation:
        members = [m for m in dict.fromkeys(member_ids) if m != creator_id]
        if not members:
            raise AppException(status_code=400, detail="Debes incluir al menos un miembro")

        # Validar jerarquía: todos los miembros deben ser "chateables" por el creador
        chatable = await self._repo.get_chatable_user_ids(creator_id)
        invalid  = [m for m in members if m not in chatable]
        if invalid:
            raise ForbiddenException("No puedes crear un chat con uno o más de estos usuarios")

        if type == "personal":
            if len(members) != 1:
                raise AppException(status_code=400, detail="Un chat personal debe tener exactamente un miembro")
            existing = await self._repo.find_personal_conversation(creator_id, members[0])
            if existing:
                return existing

        return await self._repo.create_conversation(
            type=type,
            created_by=creator_id,
            member_ids=members,
            name=name,
            description=description,
        )


class UpdateConversationUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(
        self,
        conversation_id: int,
        user_id:         int,
        name:            str | None,
        description:     str | None,
        avatar:          str | None,
    ) -> Conversation:
        conv = await self._repo.get_conversation(conversation_id, user_id)
        if not conv:
            raise _not_found()
        if conv.created_by != user_id:
            raise ForbiddenException("Solo el creador del grupo puede editarlo")
        return await self._repo.update_conversation(conversation_id, name, description, avatar)


class LeaveConversationUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(self, conversation_id: int, user_id: int) -> list[int]:
        if not await self._repo.is_member(conversation_id, user_id):
            raise ForbiddenException("No perteneces a esta conversación")
        members  = await self._repo.get_members(conversation_id)
        await self._repo.remove_member(conversation_id, user_id)
        return [m.id for m in members if m.id != user_id]


class MarkReadUseCase:
    def __init__(self, repo: IChatRepository):
        self._repo = repo

    async def execute(self, conversation_id: int, user_id: int) -> None:
        if not await self._repo.is_member(conversation_id, user_id):
            raise ForbiddenException("No perteneces a esta conversación")
        await self._repo.mark_read(conversation_id, user_id)
