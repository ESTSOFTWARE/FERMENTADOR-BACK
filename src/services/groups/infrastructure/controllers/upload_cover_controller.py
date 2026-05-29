import asyncio

import cloudinary.uploader
from fastapi import UploadFile, status

import src.core.cloudinary.config  # noqa: F401
from src.core.database import AsyncSessionLocal
from src.core.exceptions import AppException, BadRequestException
from src.services.groups.domain.dto.group_schema import GroupResponse
from src.services.groups.infrastructure.adapters.MySQL import GroupRepository

_ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
_MAX_SIZE_BYTES = 5 * 1024 * 1024


async def upload_group_cover(file: UploadFile, group_id: int) -> GroupResponse:
    if file.content_type not in _ALLOWED_TYPES:
        raise BadRequestException("Solo se permiten imágenes JPG, PNG o WEBP")

    file_bytes = await file.read()
    if len(file_bytes) > _MAX_SIZE_BYTES:
        raise BadRequestException("La imagen no puede superar los 5 MB")

    try:
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            file_bytes,
            folder="group_covers",
            resource_type="image",
        )
    except Exception as e:
        raise AppException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al subir la imagen a Cloudinary: {str(e)}",
        )

    repo  = GroupRepository(AsyncSessionLocal)
    group = await repo.update_cover(group_id=group_id, cover_image=result["secure_url"])
    return GroupResponse.from_entity(group)
