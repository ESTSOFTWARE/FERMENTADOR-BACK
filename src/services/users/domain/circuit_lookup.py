from abc import ABC, abstractmethod
from src.services.users.domain.entities.circuit_info import CircuitInfo


class ICircuitLookup(ABC):

    @abstractmethod
    async def get_by_activation_code(self, code: str) -> CircuitInfo | None:
        ...

    @abstractmethod
    async def activate(self, circuit_id: int) -> None:
        ...
