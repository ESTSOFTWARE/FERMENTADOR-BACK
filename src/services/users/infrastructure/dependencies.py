from src.core.database import AsyncSessionLocal
from src.services.users.infrastructure.adapters.postgres import UserRepository


def get_user_repository() -> UserRepository:
    return UserRepository(AsyncSessionLocal)