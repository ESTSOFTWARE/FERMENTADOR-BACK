from src.core.database import AsyncSessionLocal
from src.services.circuits.infrastructure.adapters.MySQL import CircuitRepository


def get_circuit_repository() -> CircuitRepository:
    return CircuitRepository(AsyncSessionLocal)