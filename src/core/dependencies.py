from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.exceptions import (
    AccountDeactivatedException,
    ForbiddenException,
    SessionReplacedException,
    UnauthorizedException,
)
from src.core.security import decode_token

# auto_error=False para que no falle cuando no hay header (usamos cookie)
bearer_scheme = HTTPBearer(auto_error=False)


# ── Sesión de base de datos ───────────────────────────────────────────────────
async def get_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db


# ── Usuario autenticado ───────────────────────────────────────────────────────
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict:
    # Cookie primero (web), Authorization header como fallback (mobile/API)
    token = request.cookies.get("access_token")
    if not token and credentials:
        token = credentials.credentials
    if not token:
        raise UnauthorizedException()

    payload = decode_token(token)
    user_id = payload.get("sub")
    role    = payload.get("role")

    if not user_id or not role:
        raise UnauthorizedException()

    from src.core.models.user_models import UserModel
    result = await db.execute(
        select(UserModel.is_active, UserModel.active_session_id)
        .where(UserModel.id == int(user_id))
    )
    row = result.first()
    if row is None:
        raise UnauthorizedException()
    is_active, active_session_id = row
    if is_active is False:
        raise AccountDeactivatedException()

    # ── Sesión única: el token debe corresponder a la sesión activa actual ────
    token_sid = payload.get("sid")
    if not token_sid or token_sid != active_session_id:
        raise SessionReplacedException()

    return {
        "user_id":    int(user_id),
        "role":       role,
        "circuit_id": payload.get("circuit_id"),
        "sid":        token_sid,
    }


# ── Guards de roles ───────────────────────────────────────────────────────────
async def require_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user["role"] != "admin":
        raise ForbiddenException()
    return current_user


async def require_admin_or_profesor(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user["role"] not in ("admin", "profesor"):
        raise ForbiddenException()
    return current_user


async def require_soporte(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user["role"] != "soporte":
        raise ForbiddenException()
    return current_user


async def require_admin_or_soporte(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user["role"] not in ("admin", "soporte"):
        raise ForbiddenException()
    return current_user


async def require_any_role(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user["role"] not in ("admin", "profesor", "estudiante", "soporte"):
        raise ForbiddenException()
    return current_user
