from src.core.exceptions import InvalidCredentialsException
from src.core.security import create_access_token, create_refresh_token, verify_password
from src.services.auth.domain.repository import IAuthRepository


class LoginUseCase:

    def __init__(self, repository: IAuthRepository):
        self._repo = repository

    async def execute(self, email: str, password: str) -> dict:
        user = await self._repo.get_user_by_email(email)

        if not user:
            raise InvalidCredentialsException()

        if not user.password or not verify_password(password, user.password):
            raise InvalidCredentialsException()

        role_name = user.role.name if user.role else "estudiante"

        token_data = {
            "sub":        str(user.id),
            "role":       role_name,
            "circuit_id": user.circuit_id,  # None para admins sin circuito aún
        }

        return {
            "access_token":  create_access_token(token_data),
            "refresh_token": create_refresh_token({"sub": str(user.id)}),
            "token_type":    "bearer",
            "user": {
                "id":            user.id,
                "name":          user.name,
                "last_name":     user.last_name,
                "email":         user.email,
                "role":          role_name,
                "circuit_id":    user.circuit_id,
                "profile_image": user.profile_image,
            },
        }