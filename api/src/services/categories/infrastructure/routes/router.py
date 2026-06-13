from fastapi import APIRouter, Depends

from src.core.dependencies import require_admin
from src.services.categories.domain.dto.category_schemas import (
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from src.services.categories.infrastructure.controllers.create_category_controller import create
from src.services.categories.infrastructure.controllers.delete_category_controller import delete
from src.services.categories.infrastructure.controllers.get_categories_controller import get_all
from src.services.categories.infrastructure.controllers.get_category_by_id_controller import (
    get_by_id,
)
from src.services.categories.infrastructure.controllers.update_category_controller import update

router = APIRouter()


@router.get("/", response_model=list[CategoryResponse], summary="Obtener todas las categorías")
async def get_all_categories():
    return await get_all()


@router.get("/{category_id}", response_model=CategoryResponse, summary="Obtener categoría por ID")
async def get_category(category_id: int):
    return await get_by_id(category_id)


@router.post("/", response_model=CategoryResponse, status_code=201, summary="Crear categoría (solo admin)")
async def create_category(body: CreateCategoryRequest, current_user: dict = Depends(require_admin)):
    return await create(body)


@router.put("/{category_id}", response_model=CategoryResponse, summary="Actualizar categoría (solo admin)")
async def update_category(category_id: int, body: UpdateCategoryRequest, current_user: dict = Depends(require_admin)):
    return await update(category_id, body)


@router.delete("/{category_id}", status_code=200, summary="Eliminar categoría (solo admin)")
async def delete_category(category_id: int, current_user: dict = Depends(require_admin)):
    return await delete(category_id)