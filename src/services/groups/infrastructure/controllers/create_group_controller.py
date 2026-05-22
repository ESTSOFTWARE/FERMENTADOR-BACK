from src.core.database import AsyncSessionLocal
from src.services.groups.application.usecase.create_group_use_case import CreateGroupUseCase
from src.services.groups.domain.dto.group_schema import CreateGroupRequest, GroupResponse
from src.services.groups.infrastructure.adapters.MySQL import GroupRepository


async def create_group(body: CreateGroupRequest, professor_id: int) -> GroupResponse:
    repo  = GroupRepository(AsyncSessionLocal)
    group = await CreateGroupUseCase(repo).execute(
        name=body.name,
        professor_id=professor_id,
    )
    return GroupResponse.from_entity(group)
