from sqlalchemy import delete, inspect, select
from sqlalchemy.orm import selectinload

from src.core.models.group_models import GroupMemberModel, GroupModel
from src.core.models.user_models import UserModel
from src.services.groups.domain.entities.group import Group, GroupMember
from src.services.groups.domain.repository import IGroupRepository


class GroupRepository(IGroupRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def create(self, name: str, subject: str, professor_id: int, code: str) -> Group:
        async with self._session_factory() as session:
            model = GroupModel(name=name, subject=subject, professor_id=professor_id, code=code)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return await self.get_by_id(model.id)

    async def update_cover(self, group_id: int, cover_image: str) -> Group:
        async with self._session_factory() as session:
            result = await session.execute(select(GroupModel).where(GroupModel.id == group_id))
            model = result.scalar_one_or_none()
            if model:
                model.cover_image = cover_image
                await session.commit()
        return await self.get_by_id(group_id)

    async def get_all(self) -> list[Group]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(GroupModel)
                .options(selectinload(GroupModel.professor), selectinload(GroupModel.members).selectinload(GroupMemberModel.student))
                .order_by(GroupModel.created_at.desc())
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_all_by_admin(self, admin_id: int) -> list[Group]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(GroupModel)
                .join(UserModel, GroupModel.professor_id == UserModel.id)
                .options(selectinload(GroupModel.professor), selectinload(GroupModel.members).selectinload(GroupMemberModel.student))
                .where(UserModel.created_by == admin_id)
                .order_by(GroupModel.created_at.desc())
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_all_by_professor(self, professor_id: int) -> list[Group]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(GroupModel)
                .options(selectinload(GroupModel.professor), selectinload(GroupModel.members).selectinload(GroupMemberModel.student))
                .where(GroupModel.professor_id == professor_id)
                .order_by(GroupModel.created_at.desc())
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, group_id: int) -> Group | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(GroupModel)
                .options(selectinload(GroupModel.professor), selectinload(GroupModel.members).selectinload(GroupMemberModel.student))
                .where(GroupModel.id == group_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def delete(self, group_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(GroupModel).where(GroupModel.id == group_id)
            )
            await session.commit()

    async def add_member(self, group_id: int, student_id: int) -> Group:
        async with self._session_factory() as session:
            member = GroupMemberModel(group_id=group_id, student_id=student_id)
            session.add(member)
            await session.commit()
        return await self.get_by_id(group_id)

    async def remove_member(self, group_id: int, student_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(GroupMemberModel)
                .where(GroupMemberModel.group_id == group_id)
                .where(GroupMemberModel.student_id == student_id)
            )
            await session.commit()

    async def get_all_by_student(self, student_id: int) -> list[Group]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(GroupModel)
                .join(GroupMemberModel, GroupMemberModel.group_id == GroupModel.id)
                .options(selectinload(GroupModel.professor), selectinload(GroupModel.members).selectinload(GroupMemberModel.student))
                .where(GroupMemberModel.student_id == student_id)
                .order_by(GroupModel.created_at.desc())
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def student_has_group(self, student_id: int) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(GroupMemberModel.id)
                .where(GroupMemberModel.student_id == student_id)
            )
            return result.scalar_one_or_none() is not None

    async def get_by_code(self, code: str) -> Group | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(GroupModel)
                .options(selectinload(GroupModel.professor), selectinload(GroupModel.members).selectinload(GroupMemberModel.student))
                .where(GroupModel.code == code)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    @staticmethod
    def _derive_provider(student) -> str:
        if student.oauth_google_id:
            return 'google'
        if student.oauth_github_id:
            return 'github'
        return 'email'

    def _to_entity(self, model: GroupModel) -> Group:
        return Group(
            id=model.id,
            name=model.name,
            subject=model.subject,
            cover_image=model.cover_image,
            professor_id=model.professor_id,
            professor_name=(
                f"{model.professor.name} {model.professor.last_name}"
                if "professor" not in inspect(model).unloaded and model.professor is not None
                else None
            ),
            code=model.code,
            created_at=model.created_at,
            members=[
                GroupMember(
                    id=m.id,
                    student_id=m.student_id,
                    name=m.student.name,
                    last_name=m.student.last_name,
                    email=m.student.email,
                    joined_at=m.joined_at,
                    oauth_provider=self._derive_provider(m.student),
                )
                for m in model.members
            ],
        )
