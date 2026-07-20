from src.core.database import AsyncSessionLocal
from src.services.groups.application.usecase.delete_group_use_case import DeleteGroupUseCase
from src.services.groups.infrastructure.adapters.postgres import GroupRepository


async def delete_group(group_id: int, professor_id: int, role: str = 'profesor') -> None:
    repo = GroupRepository(AsyncSessionLocal)
    await DeleteGroupUseCase(repo).execute(group_id, professor_id, role)