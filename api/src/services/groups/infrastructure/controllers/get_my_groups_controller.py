from src.core.database import AsyncSessionLocal
from src.services.groups.domain.dto.group_schema import GroupResponse
from src.services.groups.infrastructure.adapters.postgres import GroupRepository


async def get_my_groups(student_id: int) -> list[GroupResponse]:
    repo   = GroupRepository(AsyncSessionLocal)
    groups = await repo.get_all_by_student(student_id)
    return [GroupResponse.from_entity(g) for g in groups]
