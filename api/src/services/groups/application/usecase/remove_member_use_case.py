from src.core.exceptions import ForbiddenException, NotFoundException
from src.services.groups.domain.repository import IGroupRepository


class RemoveMemberUseCase:

    def __init__(self, repository: IGroupRepository):
        self._repo = repository

    async def execute(
        self,
        group_id: int,
        student_id: int,
        professor_id: int,
        role: str = 'profesor',
    ) -> None:
        group = await self._repo.get_by_id(group_id)
        if not group:
            raise NotFoundException("Grupo no encontrado")
        if role != 'admin' and group.professor_id != professor_id:
            raise ForbiddenException()

        member_ids = [m.student_id for m in group.members]
        if student_id not in member_ids:
            raise NotFoundException("El alumno no pertenece a este grupo")

        await self._repo.remove_member(group_id, student_id)