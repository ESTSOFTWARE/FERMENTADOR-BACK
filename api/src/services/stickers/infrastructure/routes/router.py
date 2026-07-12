from fastapi import APIRouter, Depends, UploadFile, File

from src.core.dependencies import require_any_role
from src.services.stickers.domain.dto.sticker_schema import (
    StickerPackDTO,
    CreateStickerPackRequest,
)

router = APIRouter()


@router.get("/packs", response_model=list[StickerPackDTO], summary="Listar sticker packs del usuario + del sistema")
async def get_packs(current_user: dict = Depends(require_any_role)):
    # TODO: return system packs + user packs from DB
    return []


@router.get("/packs/{pack_id}", response_model=StickerPackDTO, summary="Obtener un sticker pack por ID")
async def get_pack(pack_id: int, current_user: dict = Depends(require_any_role)):
    # TODO: fetch from DB
    return None


@router.post("/packs", response_model=StickerPackDTO, status_code=201, summary="Crear un sticker pack personal")
async def create_pack(
    body: CreateStickerPackRequest,
    current_user: dict = Depends(require_any_role),
):
    # TODO: create pack in DB
    return None


@router.post("/upload", summary="Subir sticker a un pack personal")
async def upload_sticker(
    pack_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(require_any_role),
):
    # TODO: upload to Cloudinary, add to pack
    return {"status": "ok"}


@router.delete("/packs/{pack_id}", status_code=204, summary="Eliminar sticker pack personal")
async def delete_pack(pack_id: int, current_user: dict = Depends(require_any_role)):
    # TODO: delete from DB
    pass
