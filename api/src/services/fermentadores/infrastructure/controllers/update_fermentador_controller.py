from src.core.database import AsyncSessionLocal
from src.services.fermentadores.application.usecase.update_fermentador_use_case import (
    UpdateFermentadorUseCase,
)
from src.services.fermentadores.domain.dto.fermentador_schema import (
    FermentadorResponse,
    UpdateFermentadorRequest,
)
from src.services.fermentadores.infrastructure.adapters.postgres import FermentadorRepository


async def update_fermentador(fermentador_id: int, body: UpdateFermentadorRequest) -> FermentadorResponse:
    repo        = FermentadorRepository(AsyncSessionLocal)
    fermentador = await UpdateFermentadorUseCase(repo).execute(
        fermentador_id,
        vendido=body.vendido,
        estado=body.estado,
        cliente_id=body.cliente_id,
    )
    return FermentadorResponse.from_entity(fermentador)
