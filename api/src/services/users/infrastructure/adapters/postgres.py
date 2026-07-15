from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
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
                .where(UserModel.is_active.is_not(False))
                .order_by(UserModel.id)
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, user_id: int) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role), selectinload(UserModel.circuit))
                .where(UserModel.id == user_id)
            )
            model = result.scalar_one_or_none()
            if not model:
                return None
            entity = self._to_entity(model)
            entity.circuit_code = model.circuit.activation_code if model.circuit else None
            return entity

    async def get_by_email(self, email: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.email == email)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_all_students(self) -> list[User]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .join(RoleModel, UserModel.role_id == RoleModel.id)
                .where(RoleModel.name == 'estudiante')
                .where(UserModel.is_active.is_not(False))
                .order_by(UserModel.name)
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_created_by(self, creator_id: int) -> list[User]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role), selectinload(UserModel.circuit))
                .where(UserModel.created_by == creator_id)
                .where(UserModel.is_active.is_not(False))
                .order_by(UserModel.id)
            )
            return [self._with_circuit_code(m) for m in result.scalars().all()]

    async def get_by_circuit_of(self, user_id: int) -> list[User]:
        """Todos los usuarios del mismo circuito que user_id (admin → ve todo su circuito)."""
        async with self._session_factory() as session:
            circuit_subq = (
                select(UserModel.circuit_id)
                .where(UserModel.id == user_id)
                .scalar_subquery()
            )
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role), selectinload(UserModel.circuit))
                .where(UserModel.circuit_id == circuit_subq)
                .where(UserModel.circuit_id.isnot(None))
                .where(UserModel.is_active.is_not(False))
                .order_by(UserModel.id)
            )
            return [self._with_circuit_code(m) for m in result.scalars().all()]

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
                    description=user.description,
                )
            )
            await session.commit()
        return await self.get_by_id(user.id)

    async def delete(self, user_id: int) -> None:
        # Soft-delete: desactiva la cuenta (no borra datos ni rompe llaves foráneas).
        # get_current_user bloquea a los is_active=False y los listados los ocultan.
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(is_active=False, active_session_id=None)
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

    async def mark_tour_completed(self, user_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(tour_completed=True)
            )
            await session.commit()

    async def deactivate_expired(self, days: int) -> int:
        threshold = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
        async with self._session_factory() as session:
            result = await session.execute(
                update(UserModel)
                .where(
                    UserModel.circuit_id == None,  # noqa: E711
                    UserModel.is_active == True,   # noqa: E712
                    UserModel.created_at <= threshold,
                )
                .values(is_active=False)
            )
            await session.commit()
            return result.rowcount

    async def reactivate(self, user_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(is_active=True)
            )
            await session.commit()

    async def get_users_for_warning_email(self, created_before: datetime) -> list[User]:
        """
        Obtiene usuarios que deben recibir el correo de advertencia.

        Condiciones:
        - is_active = TRUE
        - circuit_id = NULL
        - created_at <= created_before (hace 28 días, 2 días antes del vencimiento)
        - warning_email_sent_at = NULL (no se ha enviado aún)
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(
                    UserModel.is_active == True,  # noqa: E712
                    UserModel.circuit_id == None,  # noqa: E711
                    UserModel.created_at <= created_before,
                    UserModel.warning_email_sent_at == None,  # noqa: E711
                )
                .order_by(UserModel.id)
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def update_warning_email_sent(self, user_id: int) -> None:
        """Registra que se envió el correo de advertencia."""
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(warning_email_sent_at=datetime.utcnow())
            )
            await session.commit()

    async def update_reactivation_timestamps(
        self,
        user_id: int,
        reactivated_at: datetime,
        last_oauth_login_at: datetime,
    ) -> None:
        """Registra los timestamps de reactivación y último login OAuth."""
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(
                    reactivated_at=reactivated_at,
                    last_oauth_login_at=last_oauth_login_at,
                )
            )
            await session.commit()

    async def get_all_active_ids(self, exclude_role_ids: list[int] | None = None) -> list[int]:
        async with self._session_factory() as session:
            stmt = select(UserModel.id).where(UserModel.is_active == True)  # noqa: E712
            if exclude_role_ids:
                stmt = stmt.where(UserModel.role_id.notin_(exclude_role_ids))
            result = await session.execute(stmt)
            return list(result.scalars().all())

    def _with_circuit_code(self, model: UserModel) -> User:
        # Requiere que la query haya cargado la relación circuit (selectinload).
        entity = self._to_entity(model)
        entity.circuit_code = model.circuit.activation_code if model.circuit else None
        return entity

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
            description=model.description,
            oauth_google_id=model.oauth_google_id,
            oauth_github_id=model.oauth_github_id,
            tour_completed=model.tour_completed or False,
            is_active=model.is_active if model.is_active is not None else True,
            warning_email_sent_at=model.warning_email_sent_at,
            reactivated_at=model.reactivated_at,
            last_oauth_login_at=model.last_oauth_login_at,
        )
