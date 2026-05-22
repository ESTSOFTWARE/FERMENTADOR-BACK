from src.core.database import AsyncSessionLocal
from src.services.groups.application.usecase.get_group_by_id_use_case import GetGroupByIdUseCase
from src.services.groups.domain.dto.group_schema import GroupResponse
from src.services.groups.infrastructure.adapters.MySQL import GroupRepository


async def get_group_by_id(group_id: int, professor_id: int) -> GroupResponse:
    repo  = GroupRepository(AsyncSessionLocal)
    group = await GetGroupByIdUseCase(repo).execute(group_id, professor_id)
    return GroupResponse.from_entity(group)
