from src.core.exceptions import InvalidCredentialsException, UserNotFoundException
from src.core.security import hash_password, verify_password
from src.services.users.domain.repository import IUserRepository


class ChangePasswordUseCase:

    def __init__(self, repository: IUserRepository):
        self._repo = repository

    async def execute(self, user_id: int, current_password: str, new_password: str) -> None:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        if not user.password or not verify_password(current_password, user.password):
            raise InvalidCredentialsException()

        await self._repo.update_password(user_id, hash_password(new_password))
