from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.models.user_models import UserModel
from src.services.support.domain.repository.support_repository import SupportRepository


class SupportRepositoryMySQL(SupportRepository):
    def __init__(self, session):
        self.session = session

    async def get_admins(self) -> list[UserModel]:
        stmt = (
            select(UserModel)
            .where(UserModel.role_id == 1)
            .options(selectinload(UserModel.role))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_admin_by_id(self, admin_id: int) -> UserModel | None:
        stmt = (
            select(UserModel)
            .where(UserModel.id == admin_id)
            .where(UserModel.role_id == 1)
            .options(selectinload(UserModel.role))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
