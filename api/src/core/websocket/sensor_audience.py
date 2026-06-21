"""
Audiencia de datos de sensores por circuito.

Cuando una fermentación está corriendo **para un grupo**, sus lecturas en tiempo
real solo deben llegar a: el docente que la inició, los admins del circuito y los
alumnos miembros de ese grupo. Si no hay sesión de grupo activa, la audiencia es
`None` → se difunde a todos los del circuito (comportamiento clásico).

El resultado se cachea por circuito (se invalida al iniciar/detener fermentación)
para no consultar la BD en cada lectura.
"""
import logging

from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.core.models.group_models import GroupMemberModel
from src.core.models.user_models import UserModel

logger = logging.getLogger(__name__)

_ADMIN_ROLE_ID = 1

# circuit_id → set de user_ids permitidos | None (todos). La ausencia de la clave
# significa "no calculado todavía".
_cache: dict[int, set[int] | None] = {}


async def _compute(circuit_id: int) -> set[int] | None:
    # Import local para evitar ciclos (el adapter importa cosas de core).
    from src.services.fermentation.infrastructure.adapters import postgres as ferm

    async with AsyncSessionLocal() as session:
        row = (await session.execute(
            select(
                ferm.FermentationSessionModel.user_id,
                ferm.FermentationSessionModel.group_id,
            )
            .where(ferm.FermentationSessionModel.circuit_id == circuit_id)
            .where(ferm.FermentationSessionModel.status == "running")
            .order_by(ferm.FermentationSessionModel.id.desc())
            .limit(1)
        )).first()

        # Sin sesión corriendo o sin grupo asignado → todos (None).
        if not row or row.group_id is None:
            return None

        professor_id, group_id = row.user_id, row.group_id

        members = (await session.execute(
            select(GroupMemberModel.student_id).where(GroupMemberModel.group_id == group_id)
        )).scalars().all()

        admins = (await session.execute(
            select(UserModel.id)
            .where(UserModel.role_id == _ADMIN_ROLE_ID)
            .where(UserModel.circuit_id == circuit_id)
        )).scalars().all()

        return {professor_id, *members, *admins}


async def resolve_audience(circuit_id: int) -> set[int] | None:
    """Audiencia permitida para el circuito (cacheada). None = todos."""
    if circuit_id in _cache:
        return _cache[circuit_id]
    audience = await _compute(circuit_id)
    _cache[circuit_id] = audience
    return audience


def invalidate_audience(circuit_id: int) -> None:
    """Fuerza recálculo en la próxima lectura (al iniciar/detener fermentación)."""
    _cache.pop(circuit_id, None)
