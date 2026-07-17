import asyncio
import logging

from src.core.database import AsyncSessionLocal
from src.core.fcm.fcm_service import get_all_registered_user_ids, send_push_to_users
from src.services.fermentation.application.usecase.start_fermentation_use_case import (
    StartFermentationUseCase,
)
from src.services.fermentation.domain.dto.fermentation_session_schema import (
    FermentationSessionResponse,
)
from src.services.fermentation.domain.entities.fermentation_session import FermentationSession
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

    # Avisar a los alumnos (best-effort).
    try:
        await _notify_students(session)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"[start_fermentation] No se pudo notificar a alumnos: {e}")

    return FermentationSessionResponse.from_entity(session)


async def _notify_students(session: FermentationSession) -> None:
    group_repo = GroupRepository(AsyncSessionLocal)
    use_case   = SendNotificationUseCase(NotificationRepository(AsyncSessionLocal))

    if session.group_id is not None:
        # Fermentación asignada a un grupo → solo sus miembros.
        group = await group_repo.get_by_id(session.group_id)
        if group is None:
            return
        prof_name = group.professor_name or "El profesor"
        targets   = [
            (m.student_id, f"¡Nueva fermentación en {group.name}! El profesor {prof_name} acaba de iniciar una sesión.")
            for m in group.members
        ]
        push_body = f"¡Nueva fermentación en {group.name}!"
    else:
        # Sin grupo asignado → todos los usuarios registrados en la plataforma.
        groups    = await group_repo.get_all_by_professor(session.user_id)
        seen      = set()
        targets   = []
        prof_name = None
        for g in groups:
            if prof_name is None:
                prof_name = g.professor_name or "El profesor"
            for m in g.members:
                if m.student_id not in seen:
                    seen.add(m.student_id)
                    targets.append(
                        (m.student_id, f"¡Nueva fermentación! El profesor {prof_name} ha iniciado una sesión de fermentación.")
                    )
        push_body = "¡Nueva fermentación disponible!"

    if not targets:
        logger.warning("[start_fermentation] targets vacío — sin alumnos a notificar")
        return

    logger.warning("[start_fermentation] Notificando a %s alumnos — session=%s group=%s",
                   len(targets), session.id, session.group_id)

    # Notificaciones in-app (una por alumno).
    # push=False: el FCM se envía abajo como batch (evita un push doble por alumno).
    # return_exceptions=True: si una notificación in-app falla, las demás y el
    # push FCM de abajo siguen su curso (antes una sola excepción abortaba todo).
    inapp_tasks = [
        use_case.execute(
            user_id=uid,
            message=msg,
            notification_type="fermentation_started",
            push=False,
        )
        for uid, msg in targets
    ]
    results = await asyncio.gather(*inapp_tasks, return_exceptions=True)
    for (uid, _), res in zip(targets, results):
        if isinstance(res, Exception):
            logger.warning("[start_fermentation] Notificación in-app falló — user=%s: %s", uid, res)

    # Push FCM a todos los user_ids de este lote.
    push_user_ids = [uid for uid, _ in targets]
    if session.group_id is None:
        all_ids = await get_all_registered_user_ids()
        push_user_ids = list({*push_user_ids, *all_ids})

    logger.warning("[start_fermentation] Enviando push FCM a user_ids=%s", push_user_ids)
    await send_push_to_users(
        user_ids=push_user_ids,
        title="🍵 Nueva fermentación iniciada",
        body=push_body,
        data={"type": "fermentation_started", "session_id": str(session.id)},
    )
    logger.warning("[start_fermentation] Push FCM enviado — session=%s", session.id)
