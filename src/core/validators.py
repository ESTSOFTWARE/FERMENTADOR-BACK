import re
from typing import Annotated

from pydantic import AfterValidator

VALID_DIAL_CODES = frozenset({
    '+1', '+34', '+51', '+52', '+53', '+54', '+56', '+57', '+58',
    '+502', '+503', '+504', '+505', '+506', '+507', '+591', '+593',
    '+595', '+598', '+1-787', '+1-809',
})

_PHONE_NUMBER_RE = re.compile(r'^[0-9]{10}$')


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
