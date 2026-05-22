from src.core.database import AsyncSessionLocal
from src.services.groups.application.usecase.remove_member_use_case import RemoveMemberUseCase
from src.services.groups.infrastructure.adapters.MySQL import GroupRepository


async def remove_member(group_id: int, student_id: int, professor_id: int) -> None:
    repo = GroupRepository(AsyncSessionLocal)
    await RemoveMemberUseCase(repo).execute(group_id, student_id, professor_id)
