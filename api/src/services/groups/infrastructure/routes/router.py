from fastapi import APIRouter, Depends, File, UploadFile

from src.core.dependencies import require_admin, require_admin_or_profesor, require_any_role
from src.services.groups.domain.dto.group_schema import (
    AddMemberRequest,
    CreateGroupRequest,
    GroupResponse,
    JoinGroupRequest,
)
from src.services.groups.infrastructure.controllers.add_member_controller import add_member
from src.services.groups.infrastructure.controllers.create_group_controller import create_group
from src.services.groups.infrastructure.controllers.delete_group_controller import delete_group
from src.services.groups.infrastructure.controllers.get_group_by_id_controller import (
    get_group_by_id,
)
from src.services.groups.infrastructure.controllers.get_groups_controller import (
    get_all_groups,
    get_groups,
)
from src.services.groups.infrastructure.controllers.get_my_groups_controller import get_my_groups
from src.services.groups.infrastructure.controllers.join_group_controller import join_group
from src.services.groups.infrastructure.controllers.remove_member_controller import remove_member
from src.services.groups.infrastructure.controllers.upload_cover_controller import (
    upload_group_cover,
)

router = APIRouter()


@router.post("/", response_model=GroupResponse, status_code=201, summary="Crear grupo")
async def create_group_route(
    body: CreateGroupRequest,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await create_group(body=body, professor_id=current_user["user_id"])


@router.post("/join", response_model=GroupResponse, summary="Unirse a un grupo por código (alumno, QR/enlace)")
async def join_group_route(
    body: JoinGroupRequest,
    current_user: dict = Depends(require_any_role),
):
    return await join_group(code=body.code, student_id=current_user["user_id"])


@router.get("/me", response_model=list[GroupResponse], summary="Listar mis grupos (alumno)")
async def get_my_groups_route(current_user: dict = Depends(require_any_role)):
    return await get_my_groups(student_id=current_user["user_id"])


@router.get("/all", response_model=list[GroupResponse], summary="Listar grupos de mis docentes (solo admin)")
async def get_all_groups_route(current_user: dict = Depends(require_admin)):
    return await get_all_groups(admin_id=current_user["user_id"])


@router.get("/", response_model=list[GroupResponse], summary="Listar mis grupos")
async def get_groups_route(current_user: dict = Depends(require_admin_or_profesor)):
    return await get_groups(professor_id=current_user["user_id"])


@router.get("/{group_id}", response_model=GroupResponse, summary="Obtener grupo por ID")
async def get_group_route(
    group_id: int,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await get_group_by_id(
        group_id=group_id,
        professor_id=current_user["user_id"],
        role=current_user["role"],
    )


@router.delete("/{group_id}", status_code=204, summary="Eliminar grupo")
async def delete_group_route(
    group_id: int,
    current_user: dict = Depends(require_admin_or_profesor),
):
    await delete_group(group_id=group_id, professor_id=current_user["user_id"])


@router.post(
    "/{group_id}/members",
    response_model=GroupResponse,
    summary="Agregar alumno al grupo",
)
async def add_member_route(
    group_id: int,
    body: AddMemberRequest,
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await add_member(group_id=group_id, body=body, professor_id=current_user["user_id"])


@router.post(
    "/{group_id}/cover",
    response_model=GroupResponse,
    summary="Subir imagen de portada del grupo a Cloudinary",
)
async def upload_cover_route(
    group_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(require_admin_or_profesor),
):
    return await upload_group_cover(file=file, group_id=group_id)


@router.delete(
    "/{group_id}/members/{student_id}",
    status_code=204,
    summary="Quitar alumno del grupo",
)
async def remove_member_route(
    group_id: int,
    student_id: int,
    current_user: dict = Depends(require_admin_or_profesor),
):
    await remove_member(
        group_id=group_id,
        student_id=student_id,
        professor_id=current_user["user_id"],
    )
