from src.services.circuits.domain.entities import Circuit
from src.services.circuits.domain.repository import ICircuitRepository
from src.core.exceptions import CircuitNotFoundException


class GetCircuitStatusUseCase:

    def __init__(self, repository: ICircuitRepository):
        self._repo = repository

    async def get_by_id(self, circuit_id: int) -> Circuit:
        circuit = await self._repo.get_by_id(circuit_id)
        if not circuit:
            raise CircuitNotFoundException()
        return circuit

    async def get_by_activation_code(self, activation_code: str) -> Circuit:
        circuit = await self._repo.get_by_activation_code(activation_code)
        if not circuit:
            raise CircuitNotFoundException()
        return circuit