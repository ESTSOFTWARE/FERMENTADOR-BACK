from datetime import datetime, timedelta, timezone

from src.core.email.email_service import send_credentials_email
from src.core.exceptions import (
    ActivationCodeExpiredException,
    ForbiddenException,
    InvalidActivationCodeException,
    UserAlreadyExistsException,
)
from src.core.security import hash_password
from src.services.users.domain.circuit_lookup import ICircuitLookup
from src.services.users.domain.entities.user import User
from src.services.users.domain.repository import IUserRepository

ROLE_IDS = {"admin": 1, "profesor": 2, "estudiante": 3}

# Días antes de que un código no activado expire
EXPIRATION_DAYS = 30


class CreateUserUseCase:

    def __init__(
        self,
        user_repository:    IUserRepository,
        circuit_repository: ICircuitLookup,
    ):
        self._user_repo    = user_repository
        self._circuit_repo = circuit_repository

    async def execute(
        self,
        name:            str,
        last_name:       str,
        email:           str,
        password:        str,
        role:            str,
        created_by:      int,
        creator_role:    str,
        activation_code: str,
        dial_code:       str | None = None,
        phone_number:    str | None = None,
    ) -> User:
        # ── Validar permisos de rol ───────────────────────────────────────────
        # El profesor solo puede crear estudiantes
        if creator_role == "profesor" and role != "estudiante":
            raise ForbiddenException(
                "Los profesores solo pueden crear cuentas de tipo 'estudiante'"
            )

        # ── Límite de cuentas por plan ────────────────────────────────────────
        # El plan lo define el admin dueño de la cuenta: si crea un admin, es él;
        # si crea un profesor, es el admin que lo creó.
        from src.core.entitlements import get_user_plan, max_users

        if creator_role == "admin":
            owner_admin_id = created_by
        else:
            creator = await self._user_repo.get_by_id(created_by)
            owner_admin_id = creator.created_by if creator and creator.created_by else created_by

        plan  = await get_user_plan(owner_admin_id)
        limit = max_users(plan, role)
        label = {"admin": "administradores", "profesor": "docentes", "estudiante": "alumnos"}.get(role, role)
        if limit is not None:
            if limit == 0:
                raise ForbiddenException(
                    f"Tu plan ({plan}) no permite crear {label}. Mejora tu plan para habilitarlo."
                )
            existing = [
                u for u in await self._user_repo.get_created_by(owner_admin_id)
                if u.role_id == ROLE_IDS.get(role)
            ]
            if len(existing) >= limit:
                raise ForbiddenException(
                    f"Tu plan ({plan}) permite máximo {limit} {label}. Mejora tu plan para agregar más."
                )

        # ── Verificar email único ─────────────────────────────────────────────
        existing = await self._user_repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsException()

        # ── Validar código de activación ──────────────────────────────────────
        circuit = await self._circuit_repo.get_by_activation_code(activation_code)
        if not circuit:
            raise InvalidActivationCodeException()

        # Si el circuito nunca fue activado, verificar que no haya expirado
        if not circuit.is_active:
            expiration_threshold = datetime.now(timezone.utc) - timedelta(days=EXPIRATION_DAYS)
            if circuit.created_at and circuit.created_at.replace(tzinfo=timezone.utc) <= expiration_threshold:
                raise ActivationCodeExpiredException()

        # ── Crear usuario ─────────────────────────────────────────────────────
        new_user = User(
            id=0,
            name=name,
            last_name=last_name,
            email=email,
            password=hash_password(password),
            role_id=ROLE_IDS.get(role, 3),
            circuit_id=circuit.id,
            created_by=created_by,
            dial_code=dial_code,
            phone_number=phone_number,
        )

        # Si el circuito no estaba activo todavía, activarlo ahora
        if not circuit.is_active:
            await self._circuit_repo.activate(circuit.id)

        created = await self._user_repo.create(new_user)

        # Enviar las credenciales por correo al usuario recién creado.
        # Va con la contraseña en texto plano (la que se acaba de definir) y NO
        # debe bloquear la creación si el correo falla.
        try:
            creator = await self._user_repo.get_by_id(created_by)
            creator_name = (
                f"{creator.name} {creator.last_name}".strip()
                if creator else "Un administrador"
            )
            await send_credentials_email(
                to_email=email,
                name=name,
                creator_name=creator_name,
                role=role,
                password=password,
            )
        except Exception:  # noqa: BLE001 — el correo es best-effort
            pass

        return created