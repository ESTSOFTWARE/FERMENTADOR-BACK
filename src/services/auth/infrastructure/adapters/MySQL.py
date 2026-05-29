from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from src.core.models.user_models import RoleModel, UserModel
from src.services.auth.domain.entities.role import Role
from src.services.auth.domain.entities.user import User
from src.services.auth.domain.repository import IAuthRepository

ADMIN_ROLE_ID = 1


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
        name:         str,
        last_name:    str,
        email:        str,
        password:     str,
        role_id:      int,
        circuit_id:   int | None = None,
        dial_code:    str | None = None,
        phone_number: str | None = None,
    ) -> User:
        async with self._session_factory() as session:
            model = UserModel(
                name=name,
                last_name=last_name,
                email=email,
                password=password,
                role_id=role_id,
                circuit_id=circuit_id,
                dial_code=dial_code,
                phone_number=phone_number,
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

    async def get_user_by_google_id(self, google_id: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.oauth_google_id == google_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_user_by_github_id(self, github_id: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .where(UserModel.oauth_github_id == github_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def create_user_with_google(
        self, name: str, last_name: str, email: str, google_id: str
    ) -> User:
        async with self._session_factory() as session:
            model = UserModel(
                name=name,
                last_name=last_name,
                email=email,
                password=None,
                role_id=ADMIN_ROLE_ID,
                oauth_google_id=google_id,
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

    async def create_user_with_github(
        self, name: str, last_name: str, email: str, github_id: str
    ) -> User:
        async with self._session_factory() as session:
            model = UserModel(
                name=name,
                last_name=last_name,
                email=email,
                password=None,
                role_id=ADMIN_ROLE_ID,
                oauth_github_id=github_id,
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

    async def link_google(self, user_id: int, google_id: str) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(oauth_google_id=google_id)
            )
            await session.commit()

    async def link_github(self, user_id: int, github_id: str) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(oauth_github_id=github_id)
            )
            await session.commit()

    async def reactivate_user(self, user_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(is_active=True)
            )
            await session.commit()

    async def reactivate_user_with_notification(
        self, user_id: int, user_name: str, user_email: str
    ) -> bool:
        """Reactiva el usuario y envía correo de reactivación."""
        from datetime import datetime

        from src.core.email.email_service import send_reactivation_email

        try:
            # Enviar correo
            await send_reactivation_email(user_email, user_name)

            # Registrar timestamps de reactivación
            now = datetime.utcnow()
            async with self._session_factory() as session:
                await session.execute(
                    update(UserModel)
                    .where(UserModel.id == user_id)
                    .values(
                        is_active=True,
                        reactivated_at=now,
                        last_oauth_login_at=now,
                    )
                )
                await session.commit()

            return True

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[Reactivation] Error al reactivar usuario {user_id}: {e}")
            return False

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
            role_id=model.role_id,
            password=model.password,
            circuit_id=model.circuit_id,
            role=role,
            created_by=model.created_by,
            profile_image=model.profile_image,
            dial_code=model.dial_code,
            phone_number=model.phone_number,
            oauth_google_id=model.oauth_google_id,
            oauth_github_id=model.oauth_github_id,
            is_active=model.is_active if model.is_active is not None else True,
            warning_email_sent_at=str(model.warning_email_sent_at) if model.warning_email_sent_at else None,
            reactivated_at=str(model.reactivated_at) if model.reactivated_at else None,
            last_oauth_login_at=str(model.last_oauth_login_at) if model.last_oauth_login_at else None,
        )