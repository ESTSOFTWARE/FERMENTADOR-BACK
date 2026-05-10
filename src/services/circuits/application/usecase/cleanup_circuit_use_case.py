import logging

from src.services.circuits.domain.repository import ICircuitRepository

logger = logging.getLogger(__name__)

EXPIRATION_DAYS = 30


class CleanupExpiredCircuitsUseCase:

    def __init__(self, repository: ICircuitRepository):
        self._repo = repository

    async def execute(self) -> int:
        """
        Elimina todos los circuitos que:
        - No han sido activados (is_active = False, user_id = NULL)
        - Fueron creados hace más de EXPIRATION_DAYS días

        Retorna el número de registros eliminados.
        """
        deleted = await self._repo.delete_expired_unactivated(
            expiration_days=EXPIRATION_DAYS
        )
        if deleted:
            logger.info(
                f"[CleanupCircuits] {deleted} circuito(s) expirado(s) eliminado(s)"
            )
        else:
            logger.debug("[CleanupCircuits] No hay circuitos expirados para eliminar")
        return deleted