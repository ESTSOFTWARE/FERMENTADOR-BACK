import re
from typing import Annotated

from pydantic import AfterValidator, EmailStr

VALID_DIAL_CODES = frozenset({
    '+1', '+34', '+51', '+52', '+53', '+54', '+56', '+57', '+58',
    '+502', '+503', '+504', '+505', '+506', '+507', '+591', '+593',
    '+595', '+598', '+1-787', '+1-809',
})

_PHONE_NUMBER_RE = re.compile(r'^[0-9]{10}$')
_NAME_RE = re.compile(r"^[A-Za-zÀ-ÿ' .-]+$")


def _validate_name(v: str) -> str:
    v = (v or "").strip()
    if len(v) < 2:
        raise ValueError("Debe tener al menos 2 caracteres")
    if len(v) > 50:
        raise ValueError("No puede superar 50 caracteres")
    if not _NAME_RE.match(v):
        raise ValueError("Solo se permiten letras, espacios, apóstrofos y guiones")
    return v


def _validate_optional_name(v: str | None) -> str | None:
    return None if v is None else _validate_name(v)


def _validate_password(v: str) -> str:
    if len(v) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if len(v) > 128:
        raise ValueError("La contraseña es demasiado larga")
    if not re.search(r"[A-Za-zÀ-ÿ]", v) or not re.search(r"\d", v):
        raise ValueError("La contraseña debe incluir letras y números")
    return v


def _validate_optional_password(v: str | None) -> str | None:
    return None if v is None else _validate_password(v)


def _validate_dial_code(v: str | None) -> str | None:
    if v is None:
        return v
    if v not in VALID_DIAL_CODES:
        raise ValueError("Código de país no válido")
    return v


def _validate_phone_number(v: str | None) -> str | None:
    if v is None:
        return v
    if not _PHONE_NUMBER_RE.match(v):
        raise ValueError("El número debe tener exactamente 10 dígitos numéricos")
    return v


DialCodeStr    = Annotated[str | None, AfterValidator(_validate_dial_code)]
PhoneNumberStr = Annotated[str | None, AfterValidator(_validate_phone_number)]

# Nombre/apellido (2-50, solo letras y algunos signos).
NameStr         = Annotated[str, AfterValidator(_validate_name)]
OptionalNameStr = Annotated[str | None, AfterValidator(_validate_optional_name)]

# Contraseña (8-128, con letras y números).
PasswordStr         = Annotated[str, AfterValidator(_validate_password)]
OptionalPasswordStr = Annotated[str | None, AfterValidator(_validate_optional_password)]

# Email canonicalizado: valida formato (EmailStr) y lo normaliza a minúsculas
# sin espacios, para almacenarlo/compararlo de forma consistente.
NormalizedEmailStr = Annotated[EmailStr, AfterValidator(lambda e: e.strip().lower())]
