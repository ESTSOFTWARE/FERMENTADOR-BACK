from abc import ABC, abstractmethod
from src.services.users.domain.entities.user import User


class IUserRepository(ABC):

    @abstractmethod
    async def get_all(self) -> list[User]:
        ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    async def get_created_by(self, creator_id: int) -> list[User]:
        """Retorna todos los usuarios creados por creator_id."""
        ...

    @abstractmethod
    async def create(self, user: User) -> User:
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        ...

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        ...

    @abstractmethod
    async def assign_circuit(self, user_id: int, circuit_id: int) -> None:
        """Asigna un circuit_id al usuario."""
        ...