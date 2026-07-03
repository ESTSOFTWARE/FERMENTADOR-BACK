from src.core.database import AsyncSessionLocal
from src.services.groups.application.usecase.add_member_use_case import AddMemberUseCase
from src.services.groups.domain.dto.group_schema import AddMemberRequest, GroupResponse
from src.services.groups.infrastructure.adapters.postgres import GroupRepository
from src.services.notifications.application.usecase.send_notification_use_case import (
    SendNotificationUseCase,
)
from src.services.notifications.infrastructure.adapters.postgres import NotificationRepository
from src.services.users.infrastructure.adapters.postgres import UserRepository


async def add_member(group_id: int, body: AddMemberRequest, professor_id: int) -> GroupResponse:
    group_repo = GroupRepository(AsyncSessionLocal)
    user_repo  = UserRepository(AsyncSessionLocal)
    group      = await AddMemberUseCase(group_repo, user_repo).execute(
        group_id=group_id,
        student_id=body.student_id,
        professor_id=professor_id,
    )

    # Mensaje personalizado: quién te agregó y a qué grupo.
    prof       = await user_repo.get_by_id(professor_id)
    prof_name  = f"{prof.name} {prof.last_name}".strip() if prof else "Tu profesor"
    role_label = {1: "El administrador", 2: "El profesor"}.get(
        prof.role_id if prof else 2, "El profesor"
    )

    notif_repo = NotificationRepository(AsyncSessionLocal)
    await SendNotificationUseCase(notif_repo).execute(
        user_id=body.student_id,
        message=f"{role_label} {prof_name} te agregó a {group.name}.",
        notification_type="member_added",
    )

    return GroupResponse.from_entity(group)
