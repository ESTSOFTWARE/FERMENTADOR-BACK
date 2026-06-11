from src.core.exceptions import ForbiddenException, NotFoundException
from src.services.groups.domain.entities.group import Group
from src.services.groups.domain.repository import IGroupRepository


class GetGroupByIdUseCase:

    def __init__(self, repository: IGroupRepository):
        self._repo = repository

    async def execute(self, group_id: int, professor_id: int, role: str = 'profesor') -> Group:
        group = await self._repo.get_by_id(group_id)
        if not group:
            raise NotFoundException("Grupo no encontrado")
        if role != 'admin' and group.professor_id != professor_id:
            raise ForbiddenException()
        return group
