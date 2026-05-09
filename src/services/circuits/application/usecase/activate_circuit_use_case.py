from src.services.circuits.domain.entities.circuit import Circuit
from src.services.circuits.domain.repository import ICircuitRepository
from src.core.exceptions import CircuitNotFoundException, CircuitAlreadyActivatedException


class ActivateCircuitUseCase:

    def __init__(self, repository: ICircuitRepository):
        self._repo = repository

    async def execute(self, activation_code: str) -> Circuit:
        """
        Activa el circuito asociado al código.
        Se llama la primera vez que alguien usa el código.
        Si ya está activo, simplemente retorna el circuito (idempotente).
        """
        circuit = await self._repo.get_by_activation_code(activation_code)

        if not circuit:
            raise CircuitNotFoundException()

        if circuit.is_active:
            # Ya fue activado antes — retornamos el circuito tal cual
            return circuit

        return await self._repo.activate(circuit.id)