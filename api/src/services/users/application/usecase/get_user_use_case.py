from src.core.exceptions import UserNotFoundException
from src.services.users.domain.entities.user import User
from src.services.users.domain.repository import IUserRepository


class GetUserUseCase:

    def __init__(self, repository: IUserRepository):
        self._repo = repository

    async def get_all_students(self) -> list[User]:
        return await self._repo.get_all_students()

    async def get_all(self, requester_id: int, requester_role: str) -> list[User]:
        """
        - admin: ve TODO su circuito (admins, docentes y alumnos), incluidos los
          alumnos que crearon sus docentes — todos comparten el mismo circuit_id.
        - profesor: ve solo los usuarios que él creó directamente (sus alumnos).
        """
        if requester_role == "admin":
            return await self._repo.get_by_circuit_of(requester_id)
        return await self._repo.get_created_by(requester_id)

    async def get_by_id(self, user_id: int) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return user