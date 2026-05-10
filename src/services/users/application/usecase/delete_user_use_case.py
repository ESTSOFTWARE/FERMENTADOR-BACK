from src.core.exceptions import UserNotFoundException
from src.services.users.domain.repository import IUserRepository


class DeleteUserUseCase:

    def __init__(self, repository: IUserRepository):
        self._repo = repository

    async def execute(self, user_id: int) -> None:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        await self._repo.delete(user_id)