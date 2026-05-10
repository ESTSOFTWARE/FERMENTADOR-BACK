from datetime import datetime

from src.core.exceptions import BadRequestException
from src.services.sensors.domain.entities.sensor_reading import SensorReading
from src.services.sensors.domain.repository import ISensorRepository

VALID_SENSOR_TYPES = {
    "alcohol", "density", "conductivity",
    "ph", "temperature", "turbidity", "rpm",
}


class GetHistoryUseCase:

    def __init__(self, repository: ISensorRepository):
        self._repo = repository

    async def execute(
        self,
        circuit_id:  int,
        sensor_type: str,
        session_id:  int | None = None,
        from_dt:     datetime | None = None,
        to_dt:       datetime | None = None,
    ) -> list[SensorReading]:
        if sensor_type not in VALID_SENSOR_TYPES:
            raise BadRequestException(
                f"Tipo de sensor inválido: '{sensor_type}'. "
                f"Válidos: {', '.join(sorted(VALID_SENSOR_TYPES))}"
            )

        return await self._repo.get_history(
            circuit_id=circuit_id,
            sensor_type=sensor_type,
            session_id=session_id,
            from_dt=from_dt,
            to_dt=to_dt,
        )