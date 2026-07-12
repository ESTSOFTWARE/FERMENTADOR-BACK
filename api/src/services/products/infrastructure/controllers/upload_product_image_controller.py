from fastapi import UploadFile

from src.core.cloudinary.upload_service import upload_product_image
from src.core.database import AsyncSessionLocal
from src.services.products.application.usecase.update_product_use_case import UpdateProductUseCase
from src.services.products.domain.dto.product_schema import ProductResponse
from src.services.products.infrastructure.adapters.postgres import PostgresProductRepository


async def upload_image(product_id: int, file: UploadFile) -> ProductResponse:
    file_bytes = await file.read()
    result = await upload_product_image(file_bytes, file.content_type)

    repo = PostgresProductRepository(AsyncSessionLocal)
    product = await UpdateProductUseCase(repo).execute(product_id, image=result["secure_url"])
    return ProductResponse.from_entity(product)
