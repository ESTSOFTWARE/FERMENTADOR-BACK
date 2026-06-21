from collections import defaultdict
from datetime import datetime

from sqlalchemy import and_, delete, func, select, update

from src.core.models.chat_models import (
    ChatConversationMemberModel,
    ChatConversationModel,
    ChatMessageAttachmentModel,
    ChatMessageModel,
    ChatMessageReactionModel,
)
from src.core.models.user_models import RoleModel, UserModel
from src.services.chat.domain.entities.chat import (
    Attachment,
    Conversation,
    Member,
    Message,
    ReplyPreview,
)
from src.services.chat.domain.repository import IChatRepository


class ChatRepository(IChatRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    # ── Jerarquía ─────────────────────────────────────────────────────────────
    async def get_chatable_user_ids(self, user_id: int) -> set[int]:
        async with self._session_factory() as session:
            return await self._chatable_ids(session, user_id)

    async def _chatable_ids(self, session, user_id: int) -> set[int]:
        row = (await session.execute(
            select(UserModel.id, UserModel.created_by, RoleModel.name)
            .join(RoleModel, UserModel.role_id == RoleModel.id)
            .where(UserModel.id == user_id)
        )).first()
        if not row:
            return set()

        _, created_by, role = row

        if role == "admin":
            admin_id = user_id
        elif role == "profesor":
            admin_id = created_by
        elif role == "estudiante":
            prof = (await session.execute(
                select(UserModel.created_by).where(UserModel.id == created_by)
            )).scalar_one_or_none() if created_by else None
            admin_id = prof
        else:
            return set()

        if admin_id is None:
            return set()

        # Profesores del admin
        prof_ids = [
            r[0] for r in (await session.execute(
                select(UserModel.id).where(UserModel.created_by == admin_id)
            )).all()
        ]
        # Estudiantes de esos profesores
        student_ids = []
        if prof_ids:
            student_ids = [
                r[0] for r in (await session.execute(
                    select(UserModel.id).where(UserModel.created_by.in_(prof_ids))
                )).all()
            ]

        all_ids = {admin_id, *prof_ids, *student_ids}
        all_ids.discard(user_id)
        return all_ids

    async def get_contacts(self, user_id: int) -> list[Member]:
        async with self._session_factory() as session:
            ids = await self._chatable_ids(session, user_id)
            if not ids:
                return []
            umap = await self._users_map(session, ids)
            return [
                Member(id=uid, name=u["name"], role=u["role"], avatar=u["avatar"])
                for uid, u in umap.items()
            ]

    # ── Helpers compartidos ─────────────────────────────────────────────────────
    async def _users_map(self, session, ids: set[int] | list[int]) -> dict[int, dict]:
        ids = list(ids)
        if not ids:
            return {}
        rows = (await session.execute(
            select(
                UserModel.id, UserModel.name, UserModel.last_name,
                UserModel.profile_image, RoleModel.name,
            )
            .join(RoleModel, UserModel.role_id == RoleModel.id)
            .where(UserModel.id.in_(ids))
        )).all()
        return {
            r[0]: {"name": f"{r[1]} {r[2]}".strip(), "avatar": r[3], "role": r[4]}
            for r in rows
        }

    async def _build_messages(
        self, session, models: list[ChatMessageModel], viewer_id: int | None, last_read_at: datetime | None,
    ) -> list[Message]:
        if not models:
            return []

        msg_ids    = [m.id for m in models]
        sender_ids = {m.sender_id for m in models}
        reply_ids  = {m.reply_to_id for m in models if m.reply_to_id}

        # Attachments agrupados por message_id
        att_map: dict[int, list[Attachment]] = defaultdict(list)
        for a in (await session.execute(
            select(ChatMessageAttachmentModel).where(ChatMessageAttachmentModel.message_id.in_(msg_ids))
        )).scalars().all():
            att_map[a.message_id].append(
                Attachment(id=a.id, type=a.type, name=a.name, url=a.url, size=a.size)
            )

        # Reacciones agrupadas: message_id → emoji → [user_id]
        react_map: dict[int, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
        for r in (await session.execute(
            select(ChatMessageReactionModel).where(ChatMessageReactionModel.message_id.in_(msg_ids))
        )).scalars().all():
            react_map[r.message_id][r.emoji].append(r.user_id)

        # Previews de respuestas
        reply_map: dict[int, ReplyPreview] = {}
        if reply_ids:
            reply_models = (await session.execute(
                select(ChatMessageModel).where(ChatMessageModel.id.in_(reply_ids))
            )).scalars().all()
            reply_sender_ids = {rm.sender_id for rm in reply_models}
            reply_att = (await session.execute(
                select(ChatMessageAttachmentModel).where(
                    ChatMessageAttachmentModel.message_id.in_([rm.id for rm in reply_models])
                )
            )).scalars().all()
            first_att: dict[int, Attachment] = {}
            for a in reply_att:
                first_att.setdefault(
                    a.message_id,
                    Attachment(id=a.id, type=a.type, name=a.name, url=a.url, size=a.size),
                )
            reply_users = await self._users_map(session, sender_ids | reply_sender_ids)
            for rm in reply_models:
                ru = reply_users.get(rm.sender_id, {})
                reply_map[rm.id] = ReplyPreview(
                    id=rm.id,
                    content=None if rm.deleted else rm.content,
                    sender_name=ru.get("name", "Usuario"),
                    attachment=first_att.get(rm.id),
                )

        umap = await self._users_map(session, sender_ids)

        result = []
        for m in models:
            u = umap.get(m.sender_id, {})
            is_read = (m.sender_id == viewer_id) or (
                last_read_at is not None and m.created_at <= last_read_at
            )
            result.append(Message(
                id=m.id,
                conversation_id=m.conversation_id,
                sender_id=m.sender_id,
                sender_name=u.get("name", "Usuario"),
                sender_role=u.get("role", "estudiante"),
                content=None if m.deleted else m.content,
                created_at=m.created_at,
                read=is_read,
                deleted=bool(m.deleted),
                edited=bool(m.edited),
                edited_at=m.edited_at,
                pinned=bool(m.pinned),
                priority=m.priority,
                attachments=[] if m.deleted else att_map.get(m.id, []),
                reply_to=reply_map.get(m.reply_to_id) if m.reply_to_id else None,
                reactions={e: ids for e, ids in react_map.get(m.id, {}).items()},
            ))
        return result

    async def _members(self, session, conversation_id: int) -> list[Member]:
        rows = (await session.execute(
            select(ChatConversationMemberModel.user_id).where(
                ChatConversationMemberModel.conversation_id == conversation_id
            )
        )).all()
        ids = {r[0] for r in rows}
        umap = await self._users_map(session, ids)
        return [
            Member(id=uid, name=u["name"], role=u["role"], avatar=u["avatar"])
            for uid, u in umap.items()
        ]

    async def _last_message(self, session, conversation_id: int, viewer_id: int, last_read_at) -> Message | None:
        m = (await session.execute(
            select(ChatMessageModel)
            .where(ChatMessageModel.conversation_id == conversation_id)
            .order_by(ChatMessageModel.id.desc())
            .limit(1)
        )).scalar_one_or_none()
        if not m:
            return None
        built = await self._build_messages(session, [m], viewer_id, last_read_at)
        return built[0] if built else None

    async def _unread_count(self, session, conversation_id: int, viewer_id: int, last_read_at) -> int:
        cond = [
            ChatMessageModel.conversation_id == conversation_id,
            ChatMessageModel.sender_id != viewer_id,
            ChatMessageModel.deleted.is_(False),
        ]
        if last_read_at is not None:
            cond.append(ChatMessageModel.created_at > last_read_at)
        return (await session.execute(
            select(func.count()).select_from(ChatMessageModel).where(and_(*cond))
        )).scalar_one()

    def _conv_entity(self, model: ChatConversationModel, members, last_message, unread) -> Conversation:
        return Conversation(
            id=model.id,
            type=model.type,
            name=model.name,
            description=model.description,
            avatar=model.avatar,
            created_by=model.created_by,
            created_at=model.created_at,
            members=members,
            last_message=last_message,
            unread_count=unread,
        )

    # ── Conversaciones ────────────────────────────────────────────────────────
    async def get_conversations_for_user(self, user_id: int) -> list[Conversation]:
        async with self._session_factory() as session:
            member_rows = (await session.execute(
                select(
                    ChatConversationMemberModel.conversation_id,
                    ChatConversationMemberModel.last_read_at,
                ).where(ChatConversationMemberModel.user_id == user_id)
            )).all()
            if not member_rows:
                return []
            last_read = {r[0]: r[1] for r in member_rows}
            conv_ids  = list(last_read.keys())

            conv_models = (await session.execute(
                select(ChatConversationModel)
                .where(ChatConversationModel.id.in_(conv_ids))
                .order_by(ChatConversationModel.updated_at.desc())
            )).scalars().all()

            result = []
            for c in conv_models:
                lr = last_read.get(c.id)
                members      = await self._members(session, c.id)
                last_message = await self._last_message(session, c.id, user_id, lr)
                unread       = await self._unread_count(session, c.id, user_id, lr)
                result.append(self._conv_entity(c, members, last_message, unread))
            return result

    async def get_conversation(self, conversation_id: int, viewer_id: int) -> Conversation | None:
        async with self._session_factory() as session:
            c = (await session.execute(
                select(ChatConversationModel).where(ChatConversationModel.id == conversation_id)
            )).scalar_one_or_none()
            if not c:
                return None
            lr = (await session.execute(
                select(ChatConversationMemberModel.last_read_at).where(and_(
                    ChatConversationMemberModel.conversation_id == conversation_id,
                    ChatConversationMemberModel.user_id == viewer_id,
                ))
            )).scalar_one_or_none()
            members      = await self._members(session, conversation_id)
            last_message = await self._last_message(session, conversation_id, viewer_id, lr)
            unread       = await self._unread_count(session, conversation_id, viewer_id, lr)
            return self._conv_entity(c, members, last_message, unread)

    async def create_conversation(
        self, type, created_by, member_ids, name, description,
    ) -> Conversation:
        async with self._session_factory() as session:
            conv = ChatConversationModel(
                type=type, created_by=created_by, name=name, description=description,
            )
            session.add(conv)
            await session.flush()

            all_member_ids = {created_by, *member_ids}
            for uid in all_member_ids:
                session.add(ChatConversationMemberModel(conversation_id=conv.id, user_id=uid))
            await session.commit()
            conv_id = conv.id
        return await self.get_conversation(conv_id, created_by)

    async def find_personal_conversation(self, user_a: int, user_b: int) -> Conversation | None:
        async with self._session_factory() as session:
            ma = ChatConversationMemberModel
            sub_a = select(ma.conversation_id).where(ma.user_id == user_a)
            sub_b = select(ma.conversation_id).where(ma.user_id == user_b)
            conv_id = (await session.execute(
                select(ChatConversationModel.id)
                .where(and_(
                    ChatConversationModel.type == "personal",
                    ChatConversationModel.id.in_(sub_a),
                    ChatConversationModel.id.in_(sub_b),
                ))
                .limit(1)
            )).scalar_one_or_none()
        if conv_id is None:
            return None
        return await self.get_conversation(conv_id, user_a)

    async def update_conversation(self, conversation_id, name, description, avatar) -> Conversation:
        async with self._session_factory() as session:
            values = {}
            if name is not None:
                values["name"] = name
            if description is not None:
                values["description"] = description
            if avatar is not None:
                values["avatar"] = avatar
            if values:
                await session.execute(
                    update(ChatConversationModel)
                    .where(ChatConversationModel.id == conversation_id)
                    .values(**values)
                )
                await session.commit()
        return await self.get_conversation(conversation_id, 0)

    async def remove_member(self, conversation_id: int, user_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(ChatConversationMemberModel).where(and_(
                    ChatConversationMemberModel.conversation_id == conversation_id,
                    ChatConversationMemberModel.user_id == user_id,
                ))
            )
            await session.commit()

    async def get_members(self, conversation_id: int) -> list[Member]:
        async with self._session_factory() as session:
            return await self._members(session, conversation_id)

    async def is_member(self, conversation_id: int, user_id: int) -> bool:
        async with self._session_factory() as session:
            found = (await session.execute(
                select(ChatConversationMemberModel.id).where(and_(
                    ChatConversationMemberModel.conversation_id == conversation_id,
                    ChatConversationMemberModel.user_id == user_id,
                ))
            )).scalar_one_or_none()
            return found is not None

    # ── Mensajes ──────────────────────────────────────────────────────────────
    async def get_messages(self, conversation_id, viewer_id, cursor, limit) -> list[Message]:
        async with self._session_factory() as session:
            lr = (await session.execute(
                select(ChatConversationMemberModel.last_read_at).where(and_(
                    ChatConversationMemberModel.conversation_id == conversation_id,
                    ChatConversationMemberModel.user_id == viewer_id,
                ))
            )).scalar_one_or_none()

            stmt = select(ChatMessageModel).where(
                ChatMessageModel.conversation_id == conversation_id
            )
            if cursor is not None:
                stmt = stmt.where(ChatMessageModel.id < cursor)
            stmt = stmt.order_by(ChatMessageModel.id.desc()).limit(limit)

            models = list((await session.execute(stmt)).scalars().all())
            models.reverse()  # cronológico ascendente para el front
            return await self._build_messages(session, models, viewer_id, lr)

    async def get_message(self, message_id: int, viewer_id: int | None = None) -> Message | None:
        async with self._session_factory() as session:
            m = (await session.execute(
                select(ChatMessageModel).where(ChatMessageModel.id == message_id)
            )).scalar_one_or_none()
            if not m:
                return None
            built = await self._build_messages(session, [m], viewer_id, None)
            return built[0] if built else None

    async def create_message(
        self, conversation_id, sender_id, content, attachments, reply_to_id,
    ) -> Message:
        async with self._session_factory() as session:
            msg = ChatMessageModel(
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=content,
                reply_to_id=reply_to_id,
            )
            session.add(msg)
            await session.flush()
            for a in attachments:
                session.add(ChatMessageAttachmentModel(
                    message_id=msg.id, type=a.type, name=a.name, url=a.url, size=a.size,
                ))
            # bump updated_at de la conversación
            await session.execute(
                update(ChatConversationModel)
                .where(ChatConversationModel.id == conversation_id)
                .values(updated_at=datetime.utcnow())
            )
            await session.commit()
            msg_id = msg.id
        return await self.get_message(msg_id, sender_id)

    async def update_message_content(self, message_id: int, content: str) -> Message:
        async with self._session_factory() as session:
            await session.execute(
                update(ChatMessageModel)
                .where(ChatMessageModel.id == message_id)
                .values(content=content, edited=True, edited_at=datetime.utcnow())
            )
            await session.commit()
        return await self.get_message(message_id)

    async def soft_delete_message(self, message_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(ChatMessageModel)
                .where(ChatMessageModel.id == message_id)
                .values(deleted=True)
            )
            await session.commit()

    async def toggle_pin(self, message_id: int) -> bool:
        async with self._session_factory() as session:
            current = (await session.execute(
                select(ChatMessageModel.pinned).where(ChatMessageModel.id == message_id)
            )).scalar_one()
            new_value = not current
            await session.execute(
                update(ChatMessageModel)
                .where(ChatMessageModel.id == message_id)
                .values(pinned=new_value)
            )
            await session.commit()
            return new_value

    async def set_priority(self, message_id: int, priority: str) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(ChatMessageModel)
                .where(ChatMessageModel.id == message_id)
                .values(priority=priority)
            )
            await session.commit()

    async def toggle_reaction(self, message_id: int, user_id: int, emoji: str) -> dict[str, list[int]]:
        async with self._session_factory() as session:
            existing = (await session.execute(
                select(ChatMessageReactionModel.id).where(and_(
                    ChatMessageReactionModel.message_id == message_id,
                    ChatMessageReactionModel.user_id == user_id,
                    ChatMessageReactionModel.emoji == emoji,
                ))
            )).scalar_one_or_none()

            if existing:
                await session.execute(
                    delete(ChatMessageReactionModel).where(ChatMessageReactionModel.id == existing)
                )
            else:
                session.add(ChatMessageReactionModel(
                    message_id=message_id, user_id=user_id, emoji=emoji,
                ))
            await session.commit()

            rows = (await session.execute(
                select(ChatMessageReactionModel.emoji, ChatMessageReactionModel.user_id)
                .where(ChatMessageReactionModel.message_id == message_id)
            )).all()
        out: dict[str, list[int]] = defaultdict(list)
        for emo, uid in rows:
            out[emo].append(uid)
        return dict(out)

    async def mark_read(self, conversation_id: int, user_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(ChatConversationMemberModel)
                .where(and_(
                    ChatConversationMemberModel.conversation_id == conversation_id,
                    ChatConversationMemberModel.user_id == user_id,
                ))
                .values(last_read_at=datetime.utcnow())
            )
            await session.commit()
