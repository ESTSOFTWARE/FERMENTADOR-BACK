from sqlalchemy import text

from src.services.users.domain.circuit_lookup import ICircuitLookup
from src.services.users.domain.entities.circuit_info import CircuitInfo


class CircuitLookupAdapter(ICircuitLookup):
    """
    Consulta la tabla circuits directamente via SQL para evitar acoplamiento
    con el servicio de circuits. Solo lee/actualiza los campos que users necesita.
    """

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def get_by_activation_code(self, code: str) -> CircuitInfo | None:
        async with self._session_factory() as session:
            result = await session.execute(
                text(
                    "SELECT id, is_active, created_at "
                    "FROM circuits WHERE activation_code = :code LIMIT 1"
                ),
                {"code": code},
            )
            row = result.fetchone()
            if not row:
                return None
            return CircuitInfo(id=row[0], is_active=bool(row[1]), created_at=row[2])

    async def activate(self, circuit_id: int) -> None:
        async with self._session_factory() as session:
            await session.execute(
                text(
                    "UPDATE circuits SET is_active = TRUE, activated_at = NOW() "
                    "WHERE id = :id"
                ),
                {"id": circuit_id},
            )
            await session.commit()
