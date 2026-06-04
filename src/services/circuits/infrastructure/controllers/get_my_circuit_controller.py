from src.core.database import AsyncSessionLocal
from src.core.exceptions import CircuitNotFoundException
from src.services.circuits.application.usecase.get_circuit_status_use_case import (
    GetCircuitStatusUseCase,
)
from src.services.circuits.domain.dto.circuit_schema import CircuitResponse
from src.services.circuits.infrastructure.adapters.postgres import CircuitRepository


async def get_my_circuit(circuit_id: int) -> CircuitResponse:
    if not circuit_id:
        raise CircuitNotFoundException()
    repo = CircuitRepository(AsyncSessionLocal)
    circuit = await GetCircuitStatusUseCase(repo).get_by_id(circuit_id)
    return CircuitResponse.from_entity(circuit)
