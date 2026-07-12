from datetime import datetime
from pydantic import BaseModel, ConfigDict

_camel = ConfigDict(populate_by_name=True)


class StickerItemDTO(BaseModel):
    model_config = _camel
    id: int
    asset_url: str
    emojis: list[str] = []


class StickerPackDTO(BaseModel):
    model_config = _camel
    id: int
    identifier: str
    name: str
    tray_image: str
    stickers: list[StickerItemDTO] = []
    is_system: bool = False
    created_at: datetime | None = None


class CreateStickerPackRequest(BaseModel):
    model_config = _camel
    name: str
    tray_image: str


class UploadStickerRequest(BaseModel):
    model_config = _camel
    pack_id: int
    emojis: list[str] = []
