from datetime import datetime, timezone

from fastapi import UploadFile

from src.core.cloudinary.upload_service import upload_chat_file
from src.services.chat.domain.dto.chat_schema import UploadResponse


async def upload_file(file: UploadFile) -> UploadResponse:
    file_bytes = await file.read()
    result = await upload_chat_file(
        file_bytes=file_bytes,
        content_type=file.content_type or "",
        filename=file.filename or "archivo",
    )
    # id temporal (clave client-side); los ids reales se crean al enviar el mensaje
    temp_id = int(datetime.now(timezone.utc).timestamp() * 1000)
    return UploadResponse(
        id=temp_id,
        type=result["type"],
        name=result["name"],
        url=result["url"],
        size=result["size"],
    )
