import logging

from src.services.users.domain.repository import IUserRepository

logger = logging.getLogger(__name__)

EXPIRATION_DAYS = 30


class DeactivateExpiredUsersUseCase:

    def __init__(self, repository: IUserRepository):
        self._repo = repository

    async def execute(self) -> int:
        """
        Desactiva cuentas que:
        - Tienen circuit_id = NULL (nunca vincularon un circuito)
        - Fueron creadas hace más de EXPIRATION_DAYS días

        Retorna el número de cuentas desactivadas.
        """
        count = await self._repo.deactivate_expired(days=EXPIRATION_DAYS)
        if count:
            logger.info(f"[DeactivateUsers] {count} cuenta(s) desactivada(s) por inactividad")
        else:
            logger.debug("[DeactivateUsers] No hay cuentas expiradas para desactivar")
        return count
