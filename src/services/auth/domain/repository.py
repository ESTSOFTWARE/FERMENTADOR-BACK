from abc import ABC, abstractmethod
from datetime import datetime

from src.services.auth.domain.entities.user import User


class IAuthRepository(ABC):

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def create_user(
        self,
        name:         str,
        last_name:    str,
        email:        str,
        password:     str,
        role_id:      int,
        circuit_id:   int | None = None,
        dial_code:    str | None = None,
        phone_number: str | None = None,
    ) -> User: ...

    @abstractmethod
    async def get_user_by_google_id(self, google_id: str) -> User | None: ...

    @abstractmethod
    async def get_user_by_github_id(self, github_id: str) -> User | None: ...

    @abstractmethod
    async def create_user_with_google(
        self, name: str, last_name: str, email: str, google_id: str
    ) -> User: ...

    @abstractmethod
    async def create_user_with_github(
        self, name: str, last_name: str, email: str, github_id: str
    ) -> User: ...

    @abstractmethod
    async def link_google(self, user_id: int, google_id: str) -> None: ...

    @abstractmethod
    async def link_github(self, user_id: int, github_id: str) -> None: ...

    @abstractmethod
    async def reactivate_user(self, user_id: int) -> None: ...

    @abstractmethod
    async def reactivate_user_with_notification(
        self, user_id: int, user_name: str, user_email: str
    ) -> bool: ...

    @abstractmethod
    async def save_reset_code(
        self, user_id: int, code: str, expires_at: datetime
    ) -> None: ...

    @abstractmethod
    async def get_valid_reset_code(self, user_id: int, code: str) -> bool: ...

    @abstractmethod
    async def invalidate_reset_codes(self, user_id: int) -> None: ...

    @abstractmethod
    async def update_password(self, user_id: int, hashed_password: str) -> None: ...