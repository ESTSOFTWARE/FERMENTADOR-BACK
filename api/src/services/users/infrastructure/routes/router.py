from fastapi import APIRouter, Depends, File, UploadFile

from src.core.dependencies import require_admin, require_admin_or_profesor, require_any_role
from src.services.users.domain.dto.activate_circuit_schema import (
    ActivateCircuitRequest,
    ActivateCircuitResponse,
)
from src.services.users.domain.dto.change_password_schema import ChangePasswordRequest
from src.services.users.domain.dto.create_user_schema import CreateUserRequest
from src.services.users.domain.dto.update_user_schema import UpdateUserRequest
from src.services.users.domain.dto.user_schema import UserResponse
from src.services.users.infrastructure.controllers.activate_circuit_controller import (
    activate_my_circuit,
)
from src.services.users.infrastructure.controllers.change_password_controller import (
    change_password,
)
from src.services.users.infrastructure.controllers.create_user_controller import create
from src.services.users.infrastructure.controllers.delete_user_controller import delete
from src.services.users.infrastructure.controllers.get_all_users_controller import (
    get_all,
    get_all_students,
)
from src.services.users.infrastructure.controllers.get_user_by_id_controller import get_by_id
from src.services.users.infrastructure.controllers.mark_tour_completed_controller import (
    mark_tour_completed,
)
from src.services.users.infrastructure.controllers.update_user_controller import update
from src.services.users.infrastructure.controllers.upload_profile_image_controller import (
    upload_profile_image_controller,
)

router = APIRouter()


@router.post(
    "/me/change-password",
    summary="Cambiar contraseña del usuario autenticado",
)
async def change_password_route(
    body: ChangePasswordRequest,
    current_user: dict = Depends(require_any_role),
):
    return await change_password(user_id=current_user["user_id"], body=body)


@router.post(
    "/me/profile-image",
    summary="Subir imagen de perfil a Cloudinary",
)
async def upload_profile_image_route(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_any_role),
):
    return await upload_profile_image_controller(file, user_id=current_user["user_id"])


@router.post(
    "/me/activate",
    response_model=ActivateCircuitResponse,
    summary="Activar mi circuito con código de activación",
)
async def activate_my_circuit_route(
    body: ActivateCircuitRequest,
    current_user: dict = Depends(require_any_role),
):
    return await activate_my_circuit(user_id=current_user["user_id"], body=body)


@router.patch(
    "/me/tour",
    summary="Marcar el tour guiado como completado",
)
async def mark_tour_route(
    current_user: dict = Depends(require_any_role),
):
    return await mark_tour_completed(user_id=current_user["user_id"])


@router.get("/students", response_model=list[UserResponse], summary="Listar todos los alumnos (para agregar a grupos)")
async def get_all_students_route(current_user: dict = Depends(require_admin_or_profesor)):
    return await get_all_students()


@router.get("/", response_model=list[UserResponse], summary="Ver usuarios que yo creé")
async def get_all_users(current_user: dict = Depends(require_admin_or_profesor)):
    return await get_all(
        requester_id=current_user["user_id"],
        requester_role=current_user["role"],
    )


@router.get("/{user_id}", response_model=UserResponse, summary="Obtener usuario por ID")
async def get_user(user_id: int, current_user: dict = Depends(require_admin_or_profesor)):
    return await get_by_id(user_id)


@router.post("/", response_model=UserResponse, status_code=201, summary="Crear usuario (admin o profesor)")
async def create_user(body: CreateUserRequest, current_user: dict = Depends(require_admin_or_profesor)):
    return await create(
        body=body,
        created_by=current_user["user_id"],
        creator_role=current_user["role"],
    )


@router.put("/{user_id}", response_model=UserResponse, summary="Actualizar usuario (solo admin)")
async def update_user(user_id: int, body: UpdateUserRequest, current_user: dict = Depends(require_admin)):
    return await update(user_id, body)


@router.delete("/{user_id}", status_code=204, summary="Eliminar usuario (solo admin)")
async def delete_user(user_id: int, current_user: dict = Depends(require_admin)):
    await delete(user_id)
