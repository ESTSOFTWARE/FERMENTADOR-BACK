from src.services.groups.domain.entities.group import Group
from src.services.groups.domain.repository import IGroupRepository


class GetGroupsUseCase:

    def __init__(self, repository: IGroupRepository):
        self._repo = repository

    async def execute(self, professor_id: int) -> list[Group]:
        return await self._repo.get_all_by_professor(professor_id)
