from datetime import datetime

from fastapi import APIRouter, Depends, Query

from src.core.dependencies import require_any_role
from src.services.sensors.domain.dto.sensor_history_schema import SensorHistoryResponse
from src.services.sensors.domain.dto.sensor_reading_schema import SensorReadingResponse
from src.services.sensors.infrastructure.controllers.get_latest_reading_controller import get_latest
from src.services.sensors.infrastructure.controllers.get_sensor_history_controller import (
    get_history,
)

router = APIRouter()


@router.get(
    "/{circuit_id}/{sensor_type}/history",
    response_model=SensorHistoryResponse,
    summary="Historial de lecturas de un sensor",
)
async def get_sensor_history(
    circuit_id:  int,
    sensor_type: str,
    session_id:  int | None = Query(default=None),
    from_dt:     datetime | None = Query(default=None),
    to_dt:       datetime | None = Query(default=None),
    current_user: dict = Depends(require_any_role),
):
    return await get_history(
        circuit_id=circuit_id,
        sensor_type=sensor_type,
        session_id=session_id,
        from_dt=from_dt,
        to_dt=to_dt,
    )


@router.get(
    "/{circuit_id}/{sensor_type}/latest",
    response_model=SensorReadingResponse | None,
    summary="Última lectura de un sensor",
)
async def get_latest_reading(
    circuit_id:  int,
    sensor_type: str,
    current_user: dict = Depends(require_any_role),
):
    return await get_latest(circuit_id, sensor_type)
