from fastapi import UploadFile

from src.core.cloudinary.upload_service import upload_profile_image
from src.core.database import AsyncSessionLocal
from src.services.users.application.usecase.update_user_use_case import UpdateUserUseCase
from src.services.users.infrastructure.adapters.postgres import UserRepository


async def upload_profile_image_controller(file: UploadFile, user_id: int) -> dict:
    file_bytes = await file.read()
    result = await upload_profile_image(file_bytes, file.content_type)

    repo = UserRepository(AsyncSessionLocal)
    await UpdateUserUseCase(repo).execute(
        user_id=user_id,
        profile_image=result["secure_url"],
    )

    return {"profile_image": result["secure_url"]}
