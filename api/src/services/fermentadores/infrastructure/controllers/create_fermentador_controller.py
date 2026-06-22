from src.core.database import AsyncSessionLocal
from src.services.circuits.infrastructure.adapters.postgres import CircuitRepository
from src.services.fermentadores.application.usecase.create_fermentador_use_case import (
    CreateFermentadorUseCase,
)
from src.services.fermentadores.domain.dto.fermentador_schema import FermentadorResponse
from src.services.fermentadores.infrastructure.adapters.postgres import FermentadorRepository


async def create_fermentador(created_by: int) -> FermentadorResponse:
    repo         = FermentadorRepository(AsyncSessionLocal)
    circuit_repo = CircuitRepository(AsyncSessionLocal)
    fermentador  = await CreateFermentadorUseCase(repo, circuit_repo).execute(created_by)
    return FermentadorResponse.from_entity(fermentador)
