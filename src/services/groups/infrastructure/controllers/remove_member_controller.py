from src.core.database import AsyncSessionLocal
from src.services.groups.application.usecase.remove_member_use_case import RemoveMemberUseCase
from src.services.groups.infrastructure.adapters.MySQL import GroupRepository
from src.services.notifications.application.usecase.send_notification_use_case import (
    SendNotificationUseCase,
)
from src.services.notifications.infrastructure.adapters.MySQL import NotificationRepository


async def remove_member(group_id: int, student_id: int, professor_id: int) -> None:
    repo  = GroupRepository(AsyncSessionLocal)
    group = await repo.get_by_id(group_id)

    await RemoveMemberUseCase(repo).execute(group_id, student_id, professor_id)

    if group:
        notif_repo = NotificationRepository(AsyncSessionLocal)
        await SendNotificationUseCase(notif_repo).execute(
            user_id=student_id,
            message=f"Fuiste removido del grupo \"{group.name}\" ({group.subject}).",
            notification_type="member_removed",
        )
