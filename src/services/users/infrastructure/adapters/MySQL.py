from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload

from src.core.models.user_models import RoleModel, UserModel
from src.services.users.domain.entities.user import User
from src.services.users.domain.repository import IUserRepository


class UserRepository(IUserRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_all(self) -> list[User]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .order_by(UserModel.id)
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, user_id: int) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.id == user_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.email == email)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_created_by(self, creator_id: int) -> list[User]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.created_by == creator_id)
                .order_by(UserModel.id)
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, user: User) -> User:
        async with self._session_factory() as session:
            model = UserModel(
                name=user.name,
                last_name=user.last_name,
                email=user.email,
                password=user.password,
                role_id=user.role_id,
                circuit_id=user.circuit_id,
                created_by=user.created_by,
                dial_code=user.dial_code,
                phone_number=user.phone_number,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.id == model.id)
            )
            return self._to_entity(result.scalar_one())

    async def update(self, user: User) -> User:
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user.id)
                .values(
                    name=user.name,
                    last_name=user.last_name,
                    email=user.email,
                    password=user.password,
                    role_id=user.role_id,
                    profile_image=user.profile_image,
                    dial_code=user.dial_code,
                    phone_number=user.phone_number,
                )
            )
            await session.commit()
        return await self.get_by_id(user.id)

    async def delete(self, user_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(UserModel).where(UserModel.id == user_id)
            )
            await session.commit()

    async def update_password(self, user_id: int, hashed_password: str) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(password=hashed_password)
            )
            await session.commit()

    async def assign_circuit(self, user_id: int, circuit_id: int) -> None:
        """Asigna circuit_id al usuario. Se usa cuando el admin activa su circuito."""
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(circuit_id=circuit_id)
            )
            await session.commit()

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            name=model.name,
            last_name=model.last_name,
            email=model.email,
            password=model.password,
            role_id=model.role_id,
            circuit_id=model.circuit_id,
            role_name=model.role.name if model.role else None,
            created_by=model.created_by,
            created_at=model.created_at,
            profile_image=model.profile_image,
            dial_code=model.dial_code,
            phone_number=model.phone_number,
        )