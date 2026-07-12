import asyncio
import os

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


async def upload_product_image(file_bytes: bytes, content_type: str) -> dict:
    """Sube la imagen de un producto/componente a Cloudinary."""
    if content_type not in _ALLOWED_TYPES:
        raise BadRequestException("Solo se permiten imágenes JPG, PNG, WEBP o SVG")

    if len(file_bytes) > _MAX_SIZE_BYTES:
        raise BadRequestException("La imagen no puede superar los 5 MB")

    try:
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            file_bytes,
            folder="product_images",
            resource_type="image",
        )
    except Exception as e:
        raise AppException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al subir la imagen a Cloudinary: {str(e)}",
        ) from e

    return {
        "secure_url": result["secure_url"],
        "public_id":  result["public_id"],
    }


# ── Archivos de chat (imágenes, video, documentos, etc.) ──────────────────────
_CHAT_MAX_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

_DOCUMENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/csv",
}


_IMAGE_EXTS    = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic", ".heif", ".svg"}
_VIDEO_EXTS    = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".3gp"}
_DOCUMENT_EXTS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv"}


def _derive_chat_type(content_type: str, filename: str = "") -> str:
    """image | video | document | file según el MIME, con fallback por extensión."""
    ct = (content_type or "").lower()
    if ct.startswith("image/"):
        return "image"
    if ct.startswith("video/"):
        return "video"
    if ct in _DOCUMENT_TYPES:
        return "document"
    # Fallback por extensión (cuando el MIME viene vacío o genérico, ej. octet-stream)
    ext = os.path.splitext(filename or "")[1].lower()
    if ext in _IMAGE_EXTS:
        return "image"
    if ext in _VIDEO_EXTS:
        return "video"
    if ext in _DOCUMENT_EXTS:
        return "document"
    return "file"


async def upload_chat_file(file_bytes: bytes, content_type: str, filename: str) -> dict:
    if len(file_bytes) > _CHAT_MAX_SIZE_BYTES:
        raise BadRequestException("El archivo no puede superar los 25 MB")

    try:
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            file_bytes,
            folder="chat_files",
            resource_type="auto",
            use_filename=True,
            unique_filename=True,
        )
    except Exception as e:
        raise AppException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al subir el archivo a Cloudinary: {str(e)}",
        )

    return {
        "type":       _derive_chat_type(content_type or "", filename),
        "name":       filename,
        "url":        result["secure_url"],
        "size":       result.get("bytes", len(file_bytes)),
        "public_id":  result["public_id"],
    }
