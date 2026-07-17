import asyncio

from src.core.database import AsyncSessionLocal
from src.core.nlp.nlp_client import request_notes_generation
from src.services.fermentation.application.usecase.stop_fermentation_use_case import (
    StopFermentationUseCase,
)
from src.services.fermentation.domain.dto.fermentation_session_schema import (
    FermentationSessionResponse,
)
from src.services.fermentation.domain.dto.stop_fermentation_schema import StopFermentationRequest
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository


async def stop(
    session_id: int,
    body: StopFermentationRequest,
    user_id: int,
    bearer_token: str,
) -> FermentationSessionResponse:
    session = await StopFermentationUseCase(
        FermentationRepository(AsyncSessionLocal)
    ).execute(
        session_id     = session_id,
        interrupted_by = user_id if body.interrupted else None,
    )
    # La nota descriptiva la genera el NLP service: le reenviamos el JWT del
    # usuario y él la guarda con PATCH .../report/notes (fire-and-forget).
    asyncio.ensure_future(request_notes_generation(session_id, bearer_token))
    return FermentationSessionResponse.from_entity(session)
