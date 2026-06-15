from src.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from src.services.groups.domain.entities.group import Group
from src.services.groups.domain.repository import IGroupRepository
from src.services.users.domain.repository import IUserRepository


class JoinGroupUseCase:
    """Auto-inscripción de un alumno a un grupo mediante el código (QR / enlace)."""

    def __init__(self, group_repo: IGroupRepository, user_repo: IUserRepository):
        self._group_repo = group_repo
        self._user_repo  = user_repo

    async def execute(self, code: str, student_id: int) -> Group:
        group = await self._group_repo.get_by_code(code.strip().upper())
        if not group:
            raise NotFoundException("Código de grupo inválido")

        student = await self._user_repo.get_by_id(student_id)
        if not student:
            raise NotFoundException("Usuario no encontrado")
        if student.role_name and student.role_name.lower() != "estudiante":
            raise BadRequestException("Solo los alumnos pueden unirse a un grupo")

        # Ya es miembro de ESTE grupo → idempotente, devolver el grupo
        if any(m.student_id == student_id for m in group.members):
            return group

        # Un alumno solo puede pertenecer a un grupo a la vez
        if await self._group_repo.student_has_group(student_id):
            raise ConflictException("Ya perteneces a un grupo")

        return await self._group_repo.add_member(group.id, student_id)
