from abc import ABC, abstractmethod

from src.services.circuits.domain.entities.circuit import Circuit


class ICircuitRepository(ABC):

    @abstractmethod
    async def get_by_id(self, circuit_id: int) -> Circuit | None:
        ...

    @abstractmethod
    async def get_by_activation_code(self, code: str) -> Circuit | None:
        ...

    @abstractmethod
    async def create(self, activation_code: str) -> Circuit:
        ...

    @abstractmethod
    async def activate(self, circuit_id: int) -> Circuit:
        """Marca el circuito como activo (is_active=True, activated_at=now)."""
        ...

    @abstractmethod
    async def update_sensor_state(
        self,
        circuit_id:  int,
        sensor_type: str,
        state:       bool,
    ) -> Circuit:
        ...

    @abstractmethod
    async def update_device_state(
        self,
        circuit_id:  int,
        device_type: str,
        state:       bool,
    ) -> Circuit:
        ...

    @abstractmethod
    async def delete_expired_unactivated(self, expiration_days: int) -> int:
        """
        Elimina circuitos no activados cuyo created_at sea mayor a expiration_days.
        Retorna el número de filas eliminadas.
        """
        ...