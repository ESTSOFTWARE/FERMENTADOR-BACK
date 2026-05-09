from datetime import datetime, timezone, timedelta
from src.services.users.domain.repository import IUserRepository
from src.services.users.domain.circuit_lookup import ICircuitLookup
from src.core.security import create_access_token
from src.core.exceptions import (
    InvalidActivationCodeException,
    ActivationCodeExpiredException,
    BadRequestException,
)

EXPIRATION_DAYS = 30


class ActivateMyCircuitUseCase:

    def __init__(
        self,
        user_repository:    IUserRepository,
        circuit_repository: ICircuitLookup,
    ):
        self._user_repo    = user_repository
        self._circuit_repo = circuit_repository

    async def execute(self, user_id: int, activation_code: str) -> dict:
        """
        El admin ingresa su activation_code una sola vez.
        - Valida que el código existe y no ha expirado
        - Asigna circuit_id al usuario
        - Activa el circuito si no lo estaba
        - Devuelve un nuevo access_token con circuit_id incluido
        """
        # ── Verificar que el usuario no tenga ya un circuito asignado ─────────
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            from src.core.exceptions import UserNotFoundException
            raise UserNotFoundException()

        if user.circuit_id is not None:
            raise BadRequestException(
                "Ya tienes un circuito asignado. "
                "No puedes cambiar el código de activación."
            )

        # ── Validar el código ─────────────────────────────────────────────────
        circuit = await self._circuit_repo.get_by_activation_code(activation_code)
        if not circuit:
            raise InvalidActivationCodeException()

        # Si el circuito nunca fue activado, verificar que no haya expirado
        if not circuit.is_active:
            threshold = datetime.now(timezone.utc) - timedelta(days=EXPIRATION_DAYS)
            if circuit.created_at and circuit.created_at.replace(tzinfo=timezone.utc) <= threshold:
                raise ActivationCodeExpiredException()
            # Activar el circuito
            await self._circuit_repo.activate(circuit.id)

        # ── Asignar circuit_id al usuario ─────────────────────────────────────
        await self._user_repo.assign_circuit(user_id, circuit.id)

        # ── Generar nuevo token con circuit_id ────────────────────────────────
        new_token = create_access_token({
            "sub":        str(user_id),
            "role":       user.role_name or "admin",
            "circuit_id": circuit.id,
        })

        return {
            "access_token": new_token,
            "token_type":   "bearer",
            "circuit_id":   circuit.id,
        }