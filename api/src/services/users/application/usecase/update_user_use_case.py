from src.core.exceptions import UserAlreadyExistsException, UserNotFoundException
from src.core.security import hash_password
from src.services.users.domain.entities.user import User
from src.services.users.domain.repository import IUserRepository

ROLE_IDS = {"admin": 1, "profesor": 2, "estudiante": 3}


class UpdateUserUseCase:

    def __init__(self, repository: IUserRepository):
        self._repo = repository

    async def execute(
        self,
        user_id:       int,
        name:          str | None = None,
        last_name:     str | None = None,
        email:         str | None = None,
        password:      str | None = None,
        role:          str | None = None,
        profile_image: str | None = None,
        dial_code:    str | None = None,
        phone_number: str | None = None,
    ) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        if email and email != user.email:
            existing = await self._repo.get_by_email(email)
            if existing:
                raise UserAlreadyExistsException()

        user.name          = name          or user.name
        user.last_name     = last_name     or user.last_name
        user.email         = email         or user.email
        user.password      = hash_password(password) if password else user.password
        user.role_id       = ROLE_IDS.get(role, user.role_id) if role else user.role_id
        if profile_image is not None:
            user.profile_image = profile_image
        if dial_code is not None:
            user.dial_code = dial_code
        if phone_number is not None:
            user.phone_number = phone_number

        return await self._repo.update(user)