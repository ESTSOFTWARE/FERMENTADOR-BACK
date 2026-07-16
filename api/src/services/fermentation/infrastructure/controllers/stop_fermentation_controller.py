import asyncio

from src.core.database import AsyncSessionLocal
from src.services.fermentation.application.usecase.stop_fermentation_use_case import (
    StopFermentationUseCase,
)
from src.services.fermentation.domain.dto.fermentation_session_schema import (
    FermentationSessionResponse,
)
from src.services.fermentation.domain.dto.stop_fermentation_schema import StopFermentationRequest
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository
from src.services.fermentation.infrastructure.controllers.generate_notes_controller import (
    generate_notes,
)


async def stop(session_id: int, body: StopFermentationRequest, user_id: int) -> FermentationSessionResponse:
    session = await StopFermentationUseCase(
        FermentationRepository(AsyncSessionLocal)
    ).execute(
        session_id     = session_id,
        interrupted_by = user_id if body.interrupted else None,
    )
    asyncio.ensure_future(generate_notes(session_id, user_id))
    return FermentationSessionResponse.from_entity(session)
