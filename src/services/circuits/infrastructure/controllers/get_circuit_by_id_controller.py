from src.core.database import AsyncSessionLocal
from src.services.circuits.application.usecase.get_circuit_status_use_case import (
    GetCircuitStatusUseCase,
)
from src.services.circuits.domain.dto.circuit_schema import CircuitResponse
from src.services.circuits.infrastructure.adapters.MySQL import CircuitRepository


async def get_by_id(circuit_id: int) -> CircuitResponse:
    repo = CircuitRepository(AsyncSessionLocal)
    circuit = await GetCircuitStatusUseCase(repo).get_by_id(circuit_id)
    return CircuitResponse.from_entity(circuit)
