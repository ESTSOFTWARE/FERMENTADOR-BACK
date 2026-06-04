from src.core.database import AsyncSessionLocal
from src.services.users.application.usecase.change_password_use_case import ChangePasswordUseCase
from src.services.users.domain.dto.change_password_schema import ChangePasswordRequest
from src.services.users.infrastructure.adapters.postgres import UserRepository


async def change_password(user_id: int, body: ChangePasswordRequest) -> dict:
    repo = UserRepository(AsyncSessionLocal)
    await ChangePasswordUseCase(repo).execute(
        user_id=user_id,
        current_password=body.current_password,
        new_password=body.new_password,
    )
    return {"message": "Contraseña actualizada correctamente"}
