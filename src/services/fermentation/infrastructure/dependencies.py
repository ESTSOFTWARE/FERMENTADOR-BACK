from src.core.database import AsyncSessionLocal
from src.services.fermentation.infrastructure.adapters.MySQL import FermentationRepository


def get_fermentation_repository() -> FermentationRepository:
    return FermentationRepository(AsyncSessionLocal)