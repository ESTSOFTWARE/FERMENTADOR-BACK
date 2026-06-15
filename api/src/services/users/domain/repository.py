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
    async def get_by_circuit_of(self, user_id: int) -> list[User]:
        """Retorna todos los usuarios del mismo circuito que user_id (admin → ve todo su circuito)."""
        ...

    @abstractmethod
    async def get_all_students(self) -> list[User]:
        """Retorna todos los usuarios con rol estudiante."""
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

    @abstractmethod
    async def update_password(self, user_id: int, hashed_password: str) -> None:
        ...

    @abstractmethod
    async def mark_tour_completed(self, user_id: int) -> None:
        ...

    @abstractmethod
    async def deactivate_expired(self, days: int) -> int:
        """Desactiva cuentas con circuit_id NULL y más de `days` días de antigüedad. Retorna el total desactivado."""
        ...

    @abstractmethod
    async def reactivate(self, user_id: int) -> None:
        """Reactiva una cuenta desactivada."""
        ...

    @abstractmethod
    async def get_all_active_ids(self) -> list[int]:
        """Retorna los IDs de todos los usuarios activos."""
        ...