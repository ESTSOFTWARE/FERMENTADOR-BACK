from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.exceptions import ForbiddenException, UnauthorizedException
from src.core.security import decode_token

# ── Bearer token ──────────────────────────────────────────────────────────────
bearer_scheme = HTTPBearer()


# ── Sesión de base de datos ───────────────────────────────────────────────────
async def get_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db


# ── Usuario autenticado ───────────────────────────────────────────────────────
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Extrae y valida el token JWT del header Authorization.
    Retorna el payload completo: { sub, role, circuit_id, exp, iat }
    """
    token = credentials.credentials
    payload = decode_token(token)

    user_id = payload.get("sub")
    role    = payload.get("role")

    if not user_id or not role:
        raise UnauthorizedException()

    return {
        "user_id":    int(user_id),
        "role":       role,
        "circuit_id": payload.get("circuit_id"),  # None si no tiene circuito asignado
    }


# ── Guards de roles ───────────────────────────────────────────────────────────
async def require_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Solo admin puede acceder."""
    if current_user["role"] != "admin":
        raise ForbiddenException()
    return current_user


async def require_admin_or_profesor(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Admin y profesor pueden acceder."""
    if current_user["role"] not in ("admin", "profesor"):
        raise ForbiddenException()
    return current_user


async def require_any_role(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Cualquier usuario autenticado puede acceder."""
    if current_user["role"] not in ("admin", "profesor", "estudiante"):
        raise ForbiddenException()
    return current_user