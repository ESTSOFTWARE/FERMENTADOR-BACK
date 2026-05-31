from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.core.exceptions import ForbiddenException
from src.core.models.billing_models import SubscriptionModel

# -1 = ilimitado
PLAN_LIMITS: dict[str, dict[str, int]] = {
    "free":       {"max_circuits": 0, "max_teachers": 0},
    "starter":    {"max_circuits": 1, "max_teachers": 5},
    "academic":   {"max_circuits": 5, "max_teachers": -1},
    "enterprise": {"max_circuits": -1, "max_teachers": -1},
}

ACTIVE_STATUSES = {"active", "past_due"}


async def _get_user_plan(user_id: int, db: AsyncSession) -> str:
    result = await db.execute(
        select(SubscriptionModel.plan, SubscriptionModel.status).where(
            SubscriptionModel.user_id == user_id
        )
    )
    row = result.one_or_none()
    if not row or row.status not in ACTIVE_STATUSES:
        return "free"
    return row.plan


def get_plan_limits(plan: str) -> dict[str, int]:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])


async def require_active_subscription(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    plan = await _get_user_plan(current_user["user_id"], db)
    if plan == "free":
        raise ForbiddenException("Necesitas una suscripción activa para esta acción")
    current_user["plan"] = plan
    return current_user


async def require_plan(min_plan: str):
    order = ["starter", "academic", "enterprise"]

    async def dependency(
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        plan = await _get_user_plan(current_user["user_id"], db)
        if plan == "free" or order.index(plan) < order.index(min_plan):
            raise ForbiddenException(
                f"Necesitas el plan {min_plan} o superior para esta acción"
            )
        current_user["plan"] = plan
        return current_user

    return dependency


async def check_teacher_limit(user_id: int, current_count: int, db: AsyncSession) -> None:
    plan   = await _get_user_plan(user_id, db)
    limits = get_plan_limits(plan)
    max_t  = limits["max_teachers"]
    if max_t == 0:
        raise ForbiddenException("Necesitas una suscripción para crear docentes")
    if max_t != -1 and current_count >= max_t:
        raise ForbiddenException(
            f"Tu plan {plan} permite máximo {max_t} docente(s). Actualiza tu plan para agregar más"
        )


async def check_circuit_limit(user_id: int, current_count: int, db: AsyncSession) -> None:
    plan   = await _get_user_plan(user_id, db)
    limits = get_plan_limits(plan)
    max_c  = limits["max_circuits"]
    if max_c == 0:
        raise ForbiddenException("Necesitas una suscripción para vincular circuitos")
    if max_c != -1 and current_count >= max_c:
        raise ForbiddenException(
            f"Tu plan {plan} permite máximo {max_c} circuito(s) activo(s). Actualiza tu plan para agregar más"
        )
