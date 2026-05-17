import asyncio

import cloudinary.uploader
from fastapi import status

import src.core.cloudinary.config  # noqa: F401 — inicializa credenciales
from src.core.exceptions import AppException, BadRequestException

_ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/svg+xml"}
_MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


async def upload_profile_image(file_bytes: bytes, content_type: str) -> dict:
    if content_type not in _ALLOWED_TYPES:
        raise BadRequestException("Solo se permiten imágenes JPG, PNG, WEBP o SVG")

    if len(file_bytes) > _MAX_SIZE_BYTES:
        raise BadRequestException("La imagen no puede superar los 5 MB")

    try:
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            file_bytes,
            folder="profile_images",
            resource_type="image",
        )
    except Exception as e:
        raise AppException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al subir la imagen a Cloudinary: {str(e)}",
        )

    return {
        "secure_url": result["secure_url"],
        "public_id":  result["public_id"],
    }
