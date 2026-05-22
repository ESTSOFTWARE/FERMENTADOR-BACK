from src.core.database import AsyncSessionLocal
from src.services.groups.application.usecase.add_member_use_case import AddMemberUseCase
from src.services.groups.domain.dto.group_schema import AddMemberRequest, GroupResponse
from src.services.groups.infrastructure.adapters.MySQL import GroupRepository
from src.services.users.infrastructure.adapters.MySQL import UserRepository


async def add_member(group_id: int, body: AddMemberRequest, professor_id: int) -> GroupResponse:
    group_repo = GroupRepository(AsyncSessionLocal)
    user_repo  = UserRepository(AsyncSessionLocal)
    group      = await AddMemberUseCase(group_repo, user_repo).execute(
        group_id=group_id,
        student_id=body.student_id,
        professor_id=professor_id,
    )
    return GroupResponse.from_entity(group)
