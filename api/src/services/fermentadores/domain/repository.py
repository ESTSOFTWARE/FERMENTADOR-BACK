from abc import ABC, abstractmethod

from src.services.fermentadores.domain.entities.fermentador import Fermentador


class IFermentadorRepository(ABC):

    @abstractmethod
    async def create(self, serial: str, circuit_id: int, created_by: int | None) -> Fermentador:
        ...

    @abstractmethod
    async def get_all(self) -> list[Fermentador]:
        ...

    @abstractmethod
    async def get_by_id(self, fermentador_id: int) -> Fermentador | None:
        ...

    @abstractmethod
    async def serial_exists(self, serial: str) -> bool:
        ...

    @abstractmethod
    async def update(
        self,
        fermentador_id: int,
        vendido:    bool | None = None,
        estado:     str | None = None,
        cliente_id: int | None = None,
    ) -> Fermentador | None:
        ...
