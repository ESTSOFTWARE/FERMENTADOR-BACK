from src.core.database import AsyncSessionLocal
from src.services.fermentadores.application.usecase.get_fermentadores_use_case import (
    GetFermentadoresUseCase,
)
from src.services.fermentadores.domain.dto.fermentador_schema import FermentadorResponse
from src.services.fermentadores.infrastructure.adapters.postgres import FermentadorRepository


async def get_fermentadores() -> list[FermentadorResponse]:
    repo  = FermentadorRepository(AsyncSessionLocal)
    items = await GetFermentadoresUseCase(repo).execute()
    return [FermentadorResponse.from_entity(f) for f in items]
