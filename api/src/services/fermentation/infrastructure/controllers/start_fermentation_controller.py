import asyncio
import logging

from src.core.database import AsyncSessionLocal
from src.services.fermentation.application.usecase.start_fermentation_use_case import (
    StartFermentationUseCase,
)
from src.services.fermentation.domain.dto.fermentation_session_schema import (
    FermentationSessionResponse,
)
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository
from src.services.groups.infrastructure.adapters.postgres import GroupRepository
from src.services.notifications.application.usecase.send_notification_use_case import (
    SendNotificationUseCase,
)
from src.services.notifications.infrastructure.adapters.postgres import NotificationRepository

logger = logging.getLogger(__name__)


async def start(session_id: int) -> FermentationSessionResponse:
    session = await StartFermentationUseCase(
        FermentationRepository(AsyncSessionLocal)
    ).execute(session_id=session_id)

    # Avisar a los alumnos de las clases del profesor (best-effort).
    try:
        await _notify_students(session.user_id)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"[start_fermentation] No se pudo notificar a alumnos: {e}")

    return FermentationSessionResponse.from_entity(session)


async def _notify_students(professor_id: int) -> None:
    group_repo = GroupRepository(AsyncSessionLocal)
    use_case   = SendNotificationUseCase(NotificationRepository(AsyncSessionLocal))

    groups = await group_repo.get_all_by_professor(professor_id)
    tasks  = []
    for g in groups:
        prof_name = g.professor_name or "El profesor"
        for m in g.members:
            tasks.append(
                use_case.execute(
                    user_id=m.student_id,
                    message=f"El profesor {prof_name} ha iniciado una nueva fermentación en tu clase {g.name}.",
                    notification_type="fermentation_started",
                )
            )
    if tasks:
        await asyncio.gather(*tasks)
