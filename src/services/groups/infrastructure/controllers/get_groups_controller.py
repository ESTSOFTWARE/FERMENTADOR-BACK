from src.core.database import AsyncSessionLocal
from src.services.groups.application.usecase.get_groups_use_case import GetGroupsUseCase
from src.services.groups.domain.dto.group_schema import GroupResponse
from src.services.groups.infrastructure.adapters.MySQL import GroupRepository


async def get_groups(professor_id: int) -> list[GroupResponse]:
    repo   = GroupRepository(AsyncSessionLocal)
    groups = await GetGroupsUseCase(repo).execute(professor_id)
    return [GroupResponse.from_entity(g) for g in groups]


async def get_all_groups(admin_id: int) -> list[GroupResponse]:
    repo   = GroupRepository(AsyncSessionLocal)
    groups = await repo.get_all_by_admin(admin_id)
    return [GroupResponse.from_entity(g) for g in groups]
