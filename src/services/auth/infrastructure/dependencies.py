from src.core.database import AsyncSessionLocal
from src.services.auth.infrastructure.adapters.MySQL import AuthRepository


def get_auth_repository() -> AuthRepository:
    return AuthRepository(AsyncSessionLocal)