from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from src.core.models.group_models import GroupMemberModel, GroupModel
from src.services.groups.domain.entities.group import Group, GroupMember
from src.services.groups.domain.repository import IGroupRepository


class GroupRepository(IGroupRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def create(self, name: str, professor_id: int, code: str) -> Group:
        async with self._session_factory() as session:
            model = GroupModel(name=name, professor_id=professor_id, code=code)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return await self.get_by_id(model.id)

    async def get_all_by_professor(self, professor_id: int) -> list[Group]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(GroupModel)
                .options(selectinload(GroupModel.members).selectinload(GroupMemberModel.student))
                .where(GroupModel.professor_id == professor_id)
                .order_by(GroupModel.created_at.desc())
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, group_id: int) -> Group | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(GroupModel)
                .options(selectinload(GroupModel.members).selectinload(GroupMemberModel.student))
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
                .options(selectinload(GroupModel.members).selectinload(GroupMemberModel.student))
                .where(GroupModel.code == code)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    def _to_entity(self, model: GroupModel) -> Group:
        return Group(
            id=model.id,
            name=model.name,
            professor_id=model.professor_id,
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
                )
                for m in model.members
            ],
        )
