from src.services.fermentadores.domain.entities.fermentador import Fermentador
from src.services.fermentadores.domain.repository import IFermentadorRepository


class GetFermentadoresUseCase:

    def __init__(self, repository: IFermentadorRepository):
        self._repo = repository

    async def execute(self) -> list[Fermentador]:
        return await self._repo.get_all()
