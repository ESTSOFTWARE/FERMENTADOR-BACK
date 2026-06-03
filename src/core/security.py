"""
Hash de contraseñas: Argon2 (principal) + bcrypt (compatibilidad temporal)
JWT: access token y refresh token
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import argon2
import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from jose import ExpiredSignatureError, JWTError, jwt

from src.core.config import settings
from src.core.exceptions import TokenExpiredException, TokenInvalidException

# ── Argon2 ────────────────────────────────────────────────────────────────────
# Parámetros seguros recomendados (OWASP 2024):
#   - time_cost=3       → 3 iteraciones
#   - memory_cost=65536 → 64 MB de memoria
#   - parallelism=4     → 4 hilos en paralelo
#   - hash_len=32       → 32 bytes de output
#   - salt_len=16       → 16 bytes de salt aleatorio
_argon2_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65_536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando Argon2id.
    Usar para: registro, cambio de contraseña, reset de contraseña.
    """
    return _argon2_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash (Argon2 o bcrypt).

    Detecta automáticamente el tipo de hash:
    - Si es Argon2: valida directamente.
    - Si es bcrypt: valida con bcrypt (compatibilidad con usuarios antiguos).

    No hace rehashing; eso es responsabilidad del use case de login.
    """
    if is_bcrypt_hash(hashed_password):
        return verify_bcrypt_password(plain_password, hashed_password)
    return verify_argon2_password(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """
    Indica si el hash debe ser migrado a Argon2.
    Retorna True si es bcrypt o si los parámetros de Argon2 están desactualizados.
    """
    if is_bcrypt_hash(hashed_password):
        return True
    try:
        return _argon2_hasher.check_needs_rehash(hashed_password)
    except Exception:
        return False


# ── Helpers internos de hash ──────────────────────────────────────────────────

def is_bcrypt_hash(hashed_password: str) -> bool:
    """Detecta si un hash fue generado con bcrypt."""
    return hashed_password.startswith(("$2b$", "$2a$", "$2y$"))


def is_argon2_hash(hashed_password: str) -> bool:
    """Detecta si un hash fue generado con Argon2."""
    return hashed_password.startswith("$argon2")


def verify_bcrypt_password(plain_password: str, bcrypt_hash: str) -> bool:
    """
    Verifica una contraseña contra un hash bcrypt.
    Uso exclusivo para usuarios migrados; no generar nuevos hashes bcrypt.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            bcrypt_hash.encode("utf-8"),
        )
    except Exception:
        return False


def verify_argon2_password(plain_password: str, argon2_hash: str) -> bool:
    """Verifica una contraseña contra un hash Argon2."""
    try:
        return _argon2_hasher.verify(argon2_hash, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    except Exception:
        return False


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
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Crea un refresh token JWT de larga duración.
    data debe contener al menos: { "sub": user_id }
    """
    return _create_token(
        data=data,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
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
            algorithms=[settings.ALGORITHM],
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