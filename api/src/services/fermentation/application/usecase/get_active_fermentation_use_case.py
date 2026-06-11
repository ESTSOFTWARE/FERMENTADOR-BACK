from src.services.fermentation.domain.repository import IFermentationRepository


class GetActiveFermentationUseCase:
    def __init__(self, repository: IFermentationRepository):
        self._repo = repository

    async def execute(self, circuit_id):
        # La fermentacion activa pertenece al circuito, no al usuario.
        # Cualquier usuario con acceso al mismo circuito debe poder verla/controlarla.
        if not circuit_id:
            return None
        return await self._repo.get_active_session_by_circuit(circuit_id)
