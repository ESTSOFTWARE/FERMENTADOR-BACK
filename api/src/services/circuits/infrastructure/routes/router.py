from fastapi import APIRouter, Depends

from src.core.dependencies import (
    require_admin_or_profesor,
    require_admin_or_soporte,
    require_any_role,
)
from src.services.circuits.domain.dto.circuit_schema import CircuitResponse
from src.services.circuits.domain.dto.create_circuit_schema import CreateCircuitResponse
from src.services.circuits.infrastructure.controllers.create_circuit_controller import create
from src.services.circuits.infrastructure.controllers.get_circuit_by_id_controller import get_by_id
from src.services.circuits.infrastructure.controllers.get_my_circuit_controller import (
    get_my_circuit,
)

router = APIRouter()


@router.post(
    "/",
    response_model=CreateCircuitResponse,
    status_code=201,
    summary="Crear nuevo circuito (equipo de instalación: admin o soporte)",
)
async def create_circuit(_: dict = Depends(require_admin_or_soporte)):
    return await create()


@router.get("/me", response_model=CircuitResponse, summary="Ver mi circuito")
async def get_my_circuit_route(current_user: dict = Depends(require_any_role)):
    return await get_my_circuit(current_user.get("circuit_id"))


@router.get(
    "/{circuit_id}",
    response_model=CircuitResponse,
    summary="Ver circuito por ID (admin y profesor)",
)
async def get_circuit(circuit_id: int, current_user: dict = Depends(require_admin_or_profesor)):
    return await get_by_id(circuit_id)
