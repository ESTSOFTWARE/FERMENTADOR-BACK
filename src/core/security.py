from datetime import datetime, timedelta, timezone
from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.core.exceptions import TokenExpiredException, TokenInvalidException

# ── Bcrypt ────────────────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashea una contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT ───────────────────────────────────────────────────────────────────────
def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    """Función base para crear tokens JWT."""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    payload.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(data: dict[str, Any]) -> str:
    """
    Crea un access token JWT de corta duración.
    data debe contener al menos: { "sub": user_id, "role": role_name }
    """
    return _create_token(
        data=data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Crea un refresh token JWT de larga duración.
    data debe contener al menos: { "sub": user_id }
    """
    return _create_token(
        data=data,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodifica y valida un token JWT.
    Lanza TokenExpiredException o TokenInvalidException según el caso.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise TokenInvalidException()


def get_user_id_from_token(token: str) -> int:
    """Extrae el user_id del payload del token."""
    payload = decode_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise TokenInvalidException()
    return int(user_id)


def get_role_from_token(token: str) -> str:
    """Extrae el rol del payload del token."""
    payload = decode_token(token)
    role = payload.get("role")
    if role is None:
        raise TokenInvalidException()
    return role