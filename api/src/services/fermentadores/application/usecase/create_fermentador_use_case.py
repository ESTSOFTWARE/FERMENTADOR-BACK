import secrets
import string

from src.services.circuits.application.usecase.create_circuit_use_case import CreateCircuitUseCase
from src.services.circuits.domain.repository import ICircuitRepository
from src.services.fermentadores.domain.entities.fermentador import Fermentador
from src.services.fermentadores.domain.repository import IFermentadorRepository

_ALPHABET = string.ascii_uppercase + string.digits


class CreateFermentadorUseCase:
    """
    Registra un fermentador: genera un serial único (FRM-XXXXX), crea su circuito
    (de ahí sale el código de activación) y lo guarda con vendido=false a nombre
    del usuario de soporte que lo dio de alta.
    """

    def __init__(self, repository: IFermentadorRepository, circuit_repository: ICircuitRepository):
        self._repo = repository
        self._circuit_repo = circuit_repository

    async def execute(self, created_by: int) -> Fermentador:
        serial  = await self._generate_serial()
        circuit = await CreateCircuitUseCase(self._circuit_repo).execute()
        return await self._repo.create(serial=serial, circuit_id=circuit.id, created_by=created_by)

    async def _generate_serial(self) -> str:
        for _ in range(10):
            serial = "FRM-" + "".join(secrets.choice(_ALPHABET) for _ in range(5))
            if not await self._repo.serial_exists(serial):
                return serial
        raise RuntimeError("No se pudo generar un serial único para el fermentador")
