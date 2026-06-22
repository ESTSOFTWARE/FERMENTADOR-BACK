from src.core.exceptions import NotFoundException
from src.services.fermentadores.domain.entities.fermentador import Fermentador
from src.services.fermentadores.domain.repository import IFermentadorRepository


class UpdateFermentadorUseCase:

    def __init__(self, repository: IFermentadorRepository):
        self._repo = repository

    async def execute(
        self,
        fermentador_id: int,
        vendido:    bool | None = None,
        estado:     str | None = None,
        cliente_id: int | None = None,
    ) -> Fermentador:
        updated = await self._repo.update(fermentador_id, vendido, estado, cliente_id)
        if not updated:
            raise NotFoundException("Fermentador no encontrado")
        return updated
