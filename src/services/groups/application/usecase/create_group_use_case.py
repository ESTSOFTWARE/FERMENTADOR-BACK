import secrets

from src.services.groups.domain.entities.group import Group
from src.services.groups.domain.repository import IGroupRepository


class CreateGroupUseCase:

    def __init__(self, repository: IGroupRepository):
        self._repo = repository

    async def execute(self, name: str, professor_id: int) -> Group:
        code = secrets.token_urlsafe(6).upper()[:8]
        return await self._repo.create(name=name, professor_id=professor_id, code=code)
