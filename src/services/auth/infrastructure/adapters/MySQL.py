from sqlalchemy.orm import selectinload
from sqlalchemy import select
from src.core.models.user_models import UserModel, RoleModel
from src.services.auth.domain.entities.user import User
from src.services.auth.domain.entities.role import Role
from src.services.auth.domain.repository import IAuthRepository


# ── Repositorio ───────────────────────────────────────────────────────────────
class AuthRepository(IAuthRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_user_by_email(self, email: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.email == email)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_user_by_id(self, user_id: int) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.id == user_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def create_user(
        self,
        name:       str,
        last_name:  str,
        email:      str,
        password:   str,
        role_id:    int,
        circuit_id: int | None = None,
    ) -> User:
        async with self._session_factory() as session:
            model = UserModel(
                name=name,
                last_name=last_name,
                email=email,
                password=password,
                role_id=role_id,
                circuit_id=circuit_id,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)

            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.id == model.id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    def _to_entity(self, model: UserModel) -> User:
        role = None
        if model.role:
            role = Role(
                id=model.role.id,
                name=model.role.name,
                description=model.role.description,
            )
        return User(
            id=model.id,
            name=model.name,
            last_name=model.last_name,
            email=model.email,
            password=model.password,
            role_id=model.role_id,
            circuit_id=model.circuit_id,
            role=role,
            created_by=model.created_by,
            profile_image=model.profile_image,
        )