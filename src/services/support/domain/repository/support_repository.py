from typing import Protocol

from src.core.models.user_models import UserModel


class SupportRepository(Protocol):
    async def get_admins(self) -> list[UserModel]:
        """Obtiene la lista de todos los administradores (role_id = 1)."""
        ...

    async def get_admin_by_id(self, admin_id: int) -> UserModel | None:
        """Obtiene un administrador por su ID si tiene role_id = 1."""
        ...
