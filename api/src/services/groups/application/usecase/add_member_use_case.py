from src.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from src.services.groups.domain.entities.group import Group
from src.services.groups.domain.repository import IGroupRepository
from src.services.users.domain.repository import IUserRepository


class AddMemberUseCase:

    def __init__(self, group_repo: IGroupRepository, user_repo: IUserRepository):
        self._group_repo = group_repo
        self._user_repo  = user_repo

    async def execute(self, group_id: int, student_id: int, professor_id: int) -> Group:
        group = await self._group_repo.get_by_id(group_id)
        if not group:
            raise NotFoundException("Grupo no encontrado")
        if group.professor_id != professor_id:
            raise ForbiddenException()

        student = await self._user_repo.get_by_id(student_id)
        if not student:
            raise NotFoundException("Alumno no encontrado")
        if student.role_name and student.role_name.lower() != "estudiante":
            raise BadRequestException("Solo se pueden agregar alumnos a un grupo")

        # Un alumno puede estar en varios grupos, pero no dos veces en el mismo.
        if any(m.student_id == student_id for m in group.members):
            raise ConflictException("El alumno ya pertenece a este grupo")

        return await self._group_repo.add_member(group_id, student_id)
