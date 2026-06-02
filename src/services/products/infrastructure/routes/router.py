from fastapi import APIRouter, Depends, Query

from src.core.dependencies import require_admin
from src.services.products.domain.dto.product_schema import (
    CreateProductRequest,
    ProductResponse,
    UpdateProductRequest,
)
from src.services.products.infrastructure.controllers.create_product_controller import create
from src.services.products.infrastructure.controllers.delete_product_controller import delete
from src.services.products.infrastructure.controllers.get_product_by_id_controller import get_by_id
from src.services.products.infrastructure.controllers.get_products_controller import get_all
from src.services.products.infrastructure.controllers.update_product_controller import update

router = APIRouter()

@router.get("/", summary="Obtener todos los productos")
async def get_all_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = None
):
    return await get_all(page, limit, search)

@router.get("/{product_id}", response_model=ProductResponse, summary="Obtener producto por ID")
async def get_product(product_id: int):
    return await get_by_id(product_id)

@router.post("/", response_model=ProductResponse, status_code=201, summary="Crear producto (solo admin)")
async def create_product(body: CreateProductRequest, current_user: dict = Depends(require_admin)):
    return await create(body)

@router.put("/{product_id}", response_model=ProductResponse, summary="Actualizar producto (solo admin)")
async def update_product(product_id: int, body: UpdateProductRequest, current_user: dict = Depends(require_admin)):
    return await update(product_id, body)

@router.delete("/{product_id}", status_code=200, summary="Eliminar producto (solo admin)")
async def delete_product(product_id: int, current_user: dict = Depends(require_admin)):
    return await delete(product_id)
