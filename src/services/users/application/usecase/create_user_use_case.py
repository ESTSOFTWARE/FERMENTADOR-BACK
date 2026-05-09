from datetime import datetime, timezone, timedelta
from src.services.users.domain.entities.user import User
from src.services.users.domain.repository import IUserRepository
from src.services.users.domain.circuit_lookup import ICircuitLookup
from src.core.security import hash_password
from src.core.exceptions import (
    UserAlreadyExistsException,
    InvalidActivationCodeException,
    ActivationCodeExpiredException,
    ForbiddenException,
)

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
    ) -> User:
        # ── Validar permisos de rol ───────────────────────────────────────────
        # El profesor solo puede crear estudiantes
        if creator_role == "profesor" and role != "estudiante":
            raise ForbiddenException(
                "Los profesores solo pueden crear cuentas de tipo 'estudiante'"
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
        )

        # Si el circuito no estaba activo todavía, activarlo ahora
        if not circuit.is_active:
            await self._circuit_repo.activate(circuit.id)

        return await self._user_repo.create(new_user)