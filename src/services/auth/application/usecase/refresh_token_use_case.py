from src.core.exceptions import TokenInvalidException, UserNotFoundException
from src.core.security import create_access_token, decode_token
from src.services.auth.domain.repository import IAuthRepository


class RefreshTokenUseCase:

    def __init__(self, repository: IAuthRepository):
        self._repo = repository

    async def execute(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)

        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalidException()

        user = await self._repo.get_user_by_id(int(user_id))
        if not user:
            raise UserNotFoundException()

        return {
            "access_token": create_access_token({
                "sub":        str(user.id),
                "role":       user.role.name if user.role else "estudiante",
                "circuit_id": user.circuit_id,
            }),
            "token_type": "bearer",
        }