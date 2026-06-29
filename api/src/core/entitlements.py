"""
Entitlements (permisos) por plan de suscripción.

El plan del usuario = su suscripción ACTIVA (starter/academic/enterprise).
Sin suscripción activa → "free". Cada plan habilita un conjunto de features.

Las features bloqueadas devuelven 403 vía la dependency `require_feature(...)`
(en core/dependencies.py).
"""
import logging

from src.core.database import AsyncSessionLocal
from src.services.billing.infrastructure.adapters.postgres import BillingRepository
from src.services.users.infrastructure.adapters.postgres import UserRepository

logger = logging.getLogger(__name__)

# ── Features habilitadas por plan ───────────────────────────────────────────────
PLAN_FEATURES: dict[str, set[str]] = {
    # free: lo mínimo — ver sensores e iniciar fermentaciones.
    "free": {
        "sensors", "start_fermentation",
    },
    "starter": {
        "sensors", "start_fermentation",
        "reports", "nlp_basic", "ml_prediction",
        "user_management", "announcements",
    },
    "academic": {
        "sensors", "start_fermentation",
        "reports", "nlp_basic", "ml_prediction",
        "user_management", "announcements",
        "nlp_advanced", "genetic_algorithm", "simulator", "anomaly_detection",
    },
    "enterprise": {
        "sensors", "start_fermentation",
        "reports", "nlp_basic", "ml_prediction",
        "user_management", "announcements",
        "nlp_advanced", "genetic_algorithm", "simulator", "anomaly_detection",
        # solo Enterprise: grupos y mensajería en la plataforma
        "groups", "messaging",
        "multi_admin", "white_label", "platform_chat",
    },
}

# ── Máximo de circuitos (fermentadores) por plan. None = ilimitado ──────────────
PLAN_MAX_CIRCUITS: dict[str, int | None] = {
    "free": 1, "starter": 1, "academic": 5, "enterprise": None,
}

# ── Máximo de cuentas por plan y rol. None = ilimitado, 0 = no permitido ─────────
# Solo Enterprise puede crear administradores (multi_admin).
PLAN_USER_LIMITS: dict[str, dict[str, int | None]] = {
    "free":       {"admin": 0,    "profesor": 0,    "estudiante": 0},
    "starter":    {"admin": 0,    "profesor": 5,    "estudiante": 0},
    "academic":   {"admin": 0,    "profesor": None, "estudiante": None},
    "enterprise": {"admin": None, "profesor": None, "estudiante": None},
}

_DEFAULT_PLAN = "free"


async def get_user_plan(user_id: int) -> str:
    """
    Plan efectivo del usuario. El plan se HEREDA: si el usuario no tiene
    suscripción propia, se usa la del admin dueño de su cuenta (subiendo por
    `created_by`). Así un docente/alumno creado por un admin Enterprise también
    tiene Enterprise. 'free' si nadie en la cadena tiene suscripción activa.
    """
    try:
        billing = BillingRepository(AsyncSessionLocal)
        users   = UserRepository(AsyncSessionLocal)
        current_id: int | None = user_id
        seen: set[int] = set()
        for _ in range(6):  # tope de saltos por seguridad
            if current_id is None or current_id in seen:
                break
            seen.add(current_id)
            sub = await billing.get_by_user_id(current_id)
            if sub and sub.status == "active" and sub.plan in PLAN_FEATURES:
                return sub.plan
            user = await users.get_by_id(current_id)
            current_id = user.created_by if user else None
    except Exception as e:  # noqa: BLE001 — si falla la consulta, degradamos a free
        logger.warning(f"[entitlements] no se pudo resolver el plan del user {user_id}: {e}")
    return _DEFAULT_PLAN


def plan_allows(plan: str, feature: str) -> bool:
    return feature in PLAN_FEATURES.get(plan, PLAN_FEATURES[_DEFAULT_PLAN])


def max_circuits(plan: str) -> int | None:
    return PLAN_MAX_CIRCUITS.get(plan, PLAN_MAX_CIRCUITS[_DEFAULT_PLAN])


def max_users(plan: str, role: str) -> int | None:
    """Máximo de cuentas de `role` (profesor/estudiante) que permite el plan."""
    return PLAN_USER_LIMITS.get(plan, PLAN_USER_LIMITS[_DEFAULT_PLAN]).get(role)


async def user_has_feature(user_id: int, feature: str) -> bool:
    return plan_allows(await get_user_plan(user_id), feature)


async def get_user_entitlements(user_id: int) -> dict:
    """Entitlements completos del usuario (para que el front oculte/deshabilite UI)."""
    plan = await get_user_plan(user_id)
    return {
        "plan":         plan,
        "features":     sorted(PLAN_FEATURES.get(plan, PLAN_FEATURES[_DEFAULT_PLAN])),
        "max_circuits": max_circuits(plan),
    }
