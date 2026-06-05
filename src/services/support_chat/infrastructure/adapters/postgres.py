from collections import defaultdict
from datetime import datetime

from sqlalchemy import and_, func, select, update

from src.core.models.support_chat_models import (
    SupportConversationModel,
    SupportMessageAttachmentModel,
    SupportMessageModel,
)
from src.core.models.user_models import RoleModel, UserModel
from src.services.support_chat.domain.entities.support_chat import (
    Attachment,
    SupportConversation,
    SupportMessage,
)
from src.services.support_chat.domain.repository import ISupportChatRepository


class SupportChatRepository(ISupportChatRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    # ── Helpers ───────────────────────────────────────────────────────────────
    async def _users_map(self, session, ids: set[int]) -> dict[int, dict]:
        ids = list(ids)
        if not ids:
            return {}
        rows = (await session.execute(
            select(UserModel.id, UserModel.name, UserModel.last_name, UserModel.email)
            .where(UserModel.id.in_(ids))
        )).all()
        return {
            r[0]: {"name": f"{r[1]} {r[2]}".strip(), "email": r[3]}
            for r in rows
        }

    @staticmethod
    def _last_read_column(viewer_role: str):
        return (
            SupportConversationModel.last_read_support_at
            if viewer_role == "soporte"
            else SupportConversationModel.last_read_admin_at
        )

    async def _build_messages(
        self, session, models: list[SupportMessageModel], viewer_role: str, last_read: datetime | None,
    ) -> list[SupportMessage]:
        if not models:
            return []
        msg_ids    = [m.id for m in models]
        sender_ids = {m.sender_id for m in models}

        att_map: dict[int, list[Attachment]] = defaultdict(list)
        for a in (await session.execute(
            select(SupportMessageAttachmentModel).where(SupportMessageAttachmentModel.message_id.in_(msg_ids))
        )).scalars().all():
            att_map[a.message_id].append(
                Attachment(id=a.id, type=a.type, name=a.name, url=a.url, size=a.size)
            )

        umap = await self._users_map(session, sender_ids)

        result = []
        for m in models:
            u = umap.get(m.sender_id, {})
            # Leído si el viewer es el autor, o el mensaje es anterior a su último read
            is_read = (m.sender_role == viewer_role) or (
                last_read is not None and m.created_at <= last_read
            )
            result.append(SupportMessage(
                id=m.id,
                conversation_id=m.conversation_id,
                sender_id=m.sender_id,
                sender_name=u.get("name", "Usuario"),
                sender_role=m.sender_role,
                content=m.content,
                created_at=m.created_at,
                read=is_read,
                attachments=att_map.get(m.id, []),
            ))
        return result

    async def _last_message(self, session, conversation_id, viewer_role, last_read) -> SupportMessage | None:
        m = (await session.execute(
            select(SupportMessageModel)
            .where(SupportMessageModel.conversation_id == conversation_id)
            .order_by(SupportMessageModel.id.desc())
            .limit(1)
        )).scalar_one_or_none()
        if not m:
            return None
        built = await self._build_messages(session, [m], viewer_role, last_read)
        return built[0] if built else None

    async def _unread_count(self, session, conversation_id, viewer_role, last_read) -> int:
        cond = [
            SupportMessageModel.conversation_id == conversation_id,
            SupportMessageModel.sender_role != viewer_role,  # mensajes del otro lado
        ]
        if last_read is not None:
            cond.append(SupportMessageModel.created_at > last_read)
        return (await session.execute(
            select(func.count()).select_from(SupportMessageModel).where(and_(*cond))
        )).scalar_one()

    def _conv_entity(self, model, admin, last_message, unread) -> SupportConversation:
        return SupportConversation(
            id=model.id,
            admin_id=model.admin_id,
            admin_name=admin.get("name", "Admin"),
            admin_email=admin.get("email", ""),
            created_at=model.created_at,
            last_message=last_message,
            unread_count=unread,
        )

    # ── Conversaciones ────────────────────────────────────────────────────────
    async def get_or_create_for_admin(self, admin_id: int) -> tuple[SupportConversation, bool]:
        async with self._session_factory() as session:
            conv = (await session.execute(
                select(SupportConversationModel).where(SupportConversationModel.admin_id == admin_id)
            )).scalar_one_or_none()
            created = False
            if not conv:
                conv = SupportConversationModel(admin_id=admin_id)
                session.add(conv)
                await session.commit()
                await session.refresh(conv)
                created = True

            admin = (await self._users_map(session, {admin_id})).get(admin_id, {})
            last_message = await self._last_message(session, conv.id, "admin", conv.last_read_admin_at)
            unread       = await self._unread_count(session, conv.id, "admin", conv.last_read_admin_at)
            return self._conv_entity(conv, admin, last_message, unread), created

    async def get_conversation(self, conversation_id: int, viewer_role: str) -> SupportConversation | None:
        async with self._session_factory() as session:
            conv = (await session.execute(
                select(SupportConversationModel).where(SupportConversationModel.id == conversation_id)
            )).scalar_one_or_none()
            if not conv:
                return None
            last_read = conv.last_read_support_at if viewer_role == "soporte" else conv.last_read_admin_at
            admin = (await self._users_map(session, {conv.admin_id})).get(conv.admin_id, {})
            last_message = await self._last_message(session, conv.id, viewer_role, last_read)
            unread       = await self._unread_count(session, conv.id, viewer_role, last_read)
            return self._conv_entity(conv, admin, last_message, unread)

    async def list_conversations(self) -> list[SupportConversation]:
        async with self._session_factory() as session:
            convs = (await session.execute(
                select(SupportConversationModel).order_by(SupportConversationModel.updated_at.desc())
            )).scalars().all()
            if not convs:
                return []
            admins = await self._users_map(session, {c.admin_id for c in convs})
            result = []
            for c in convs:
                admin = admins.get(c.admin_id, {})
                last_message = await self._last_message(session, c.id, "soporte", c.last_read_support_at)
                unread       = await self._unread_count(session, c.id, "soporte", c.last_read_support_at)
                result.append(self._conv_entity(c, admin, last_message, unread))
            return result

    async def is_admin_owner(self, conversation_id: int, admin_id: int) -> bool:
        async with self._session_factory() as session:
            owner = (await session.execute(
                select(SupportConversationModel.admin_id).where(SupportConversationModel.id == conversation_id)
            )).scalar_one_or_none()
            return owner == admin_id

    async def get_admin_id(self, conversation_id: int) -> int | None:
        async with self._session_factory() as session:
            return (await session.execute(
                select(SupportConversationModel.admin_id).where(SupportConversationModel.id == conversation_id)
            )).scalar_one_or_none()

    async def get_support_agent_ids(self) -> list[int]:
        async with self._session_factory() as session:
            rows = (await session.execute(
                select(UserModel.id)
                .join(RoleModel, UserModel.role_id == RoleModel.id)
                .where(RoleModel.name == "soporte")
            )).all()
            return [r[0] for r in rows]

    # ── Mensajes ──────────────────────────────────────────────────────────────
    async def get_messages(self, conversation_id, viewer_role, cursor, limit) -> list[SupportMessage]:
        async with self._session_factory() as session:
            conv = (await session.execute(
                select(SupportConversationModel).where(SupportConversationModel.id == conversation_id)
            )).scalar_one_or_none()
            last_read = None
            if conv:
                last_read = conv.last_read_support_at if viewer_role == "soporte" else conv.last_read_admin_at

            stmt = select(SupportMessageModel).where(
                SupportMessageModel.conversation_id == conversation_id
            )
            if cursor is not None:
                stmt = stmt.where(SupportMessageModel.id < cursor)
            stmt = stmt.order_by(SupportMessageModel.id.desc()).limit(limit)

            models = list((await session.execute(stmt)).scalars().all())
            models.reverse()
            return await self._build_messages(session, models, viewer_role, last_read)

    async def create_message(
        self, conversation_id, sender_id, sender_role, content, attachments,
    ) -> SupportMessage:
        async with self._session_factory() as session:
            msg = SupportMessageModel(
                conversation_id=conversation_id,
                sender_id=sender_id,
                sender_role=sender_role,
                content=content,
            )
            session.add(msg)
            await session.flush()
            for a in attachments:
                session.add(SupportMessageAttachmentModel(
                    message_id=msg.id, type=a.type, name=a.name, url=a.url, size=a.size,
                ))
            await session.execute(
                update(SupportConversationModel)
                .where(SupportConversationModel.id == conversation_id)
                .values(updated_at=datetime.utcnow())
            )
            await session.commit()
            msg_id = msg.id

            m = (await session.execute(
                select(SupportMessageModel).where(SupportMessageModel.id == msg_id)
            )).scalar_one()
            built = await self._build_messages(session, [m], sender_role, None)
            return built[0]

    async def mark_read(self, conversation_id: int, viewer_role: str) -> None:
        async with self._session_factory() as session:
            col = "last_read_support_at" if viewer_role == "soporte" else "last_read_admin_at"
            await session.execute(
                update(SupportConversationModel)
                .where(SupportConversationModel.id == conversation_id)
                .values(**{col: datetime.utcnow()})
            )
            await session.commit()
