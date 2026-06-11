from datetime import datetime

from src.core.database import AsyncSessionLocal
from src.services.sensors.application.usecase.get_history_use_case import GetHistoryUseCase
from src.services.sensors.domain.dto.sensor_history_schema import SensorHistoryResponse
from src.services.sensors.domain.dto.sensor_reading_schema import SensorReadingResponse
from src.services.sensors.infrastructure.adapters.postgres import SensorRepository


async def get_history(
    circuit_id:  int,
    sensor_type: str,
    session_id:  int | None = None,
    from_dt:     datetime | None = None,
    to_dt:       datetime | None = None,
) -> SensorHistoryResponse:
    repo = SensorRepository(AsyncSessionLocal)
    readings = await GetHistoryUseCase(repo).execute(
        circuit_id=circuit_id,
        sensor_type=sensor_type,
        session_id=session_id,
        from_dt=from_dt,
        to_dt=to_dt,
    )
    return SensorHistoryResponse(
        circuit_id=circuit_id,
        sensor_type=sensor_type,
        readings=[SensorReadingResponse.from_entity(r) for r in readings],
    )
