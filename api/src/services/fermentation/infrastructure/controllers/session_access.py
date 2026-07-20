"""
Control de acceso a una sesión de fermentación de grupo.

Una sesión con group_id solo la ven/usan: el docente que la creó, los admins
y los miembros de ese grupo. Sin group_id (o sin user) el acceso es libre —
comportamiento clásico por circuito.
"""
from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.core.models.group_models import GroupMemberModel
from src.core.models.user_models import UserModel

_ADMIN_ROLE_ID = 1


async def user_can_access_session(session_entity, user_id: int | None) -> bool:
    if session_entity.group_id is None or user_id is None:
        return True
    if user_id == session_entity.user_id:
        return True

    async with AsyncSessionLocal() as db:
        is_member = (await db.execute(
            select(GroupMemberModel.student_id)
            .where(GroupMemberModel.group_id == session_entity.group_id)
            .where(GroupMemberModel.student_id == user_id)
        )).first()
        if is_member:
            return True

        is_admin = (await db.execute(
            select(UserModel.id)
            .where(UserModel.id == user_id)
            .where(UserModel.role_id == _ADMIN_ROLE_ID)
        )).first()
        return bool(is_admin)
