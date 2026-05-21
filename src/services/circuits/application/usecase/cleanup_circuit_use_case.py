import logging

from src.services.circuits.domain.repository import ICircuitRepository

logger = logging.getLogger(__name__)

EXPIRATION_DAYS = 30


class CleanupExpiredCircuitsUseCase:

    def __init__(self, repository: ICircuitRepository):
        self._repo = repository

    async def execute(self) -> int:
        """
        Deshabilitado: los circuitos representan dispositivos físicos y no deben
        eliminarse automáticamente. La limpieza ahora opera sobre cuentas de usuario
        (DeactivateExpiredUsersUseCase).
        """
        logger.debug("[CleanupCircuits] Deshabilitado — los circuitos son dispositivos físicos")
        return 0