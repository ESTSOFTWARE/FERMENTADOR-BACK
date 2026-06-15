import logging

from src.core.database import AsyncSessionLocal
from src.services.groups.application.usecase.join_group_use_case import JoinGroupUseCase
from src.services.groups.domain.dto.group_schema import GroupResponse
from src.services.groups.infrastructure.adapters.postgres import GroupRepository
from src.services.notifications.application.usecase.send_notification_use_case import (
    SendNotificationUseCase,
)
from src.services.notifications.infrastructure.adapters.postgres import NotificationRepository
from src.services.users.infrastructure.adapters.postgres import UserRepository

logger = logging.getLogger(__name__)


async def join_group(code: str, student_id: int) -> GroupResponse:
    group_repo = GroupRepository(AsyncSessionLocal)
    user_repo  = UserRepository(AsyncSessionLocal)
    group      = await JoinGroupUseCase(group_repo, user_repo).execute(
        code=code,
        student_id=student_id,
    )

    # Avisar al profesor (best-effort: no debe romper la unión)
    try:
        notif_repo   = NotificationRepository(AsyncSessionLocal)
        student      = await user_repo.get_by_id(student_id)
        student_name = f"{student.name} {student.last_name}" if student else "Un alumno"
        await SendNotificationUseCase(notif_repo).execute(
            user_id=group.professor_id,
            message=f"{student_name} se unió a tu grupo \"{group.name}\".",
            notification_type="member_added",
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"[join_group] No se pudo notificar al profesor: {e}")

    return GroupResponse.from_entity(group)
