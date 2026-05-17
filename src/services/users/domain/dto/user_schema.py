from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id:            int
    name:          str
    last_name:     str
    email:         str
    role_id:       int
    role_name:     str | None
    circuit_id:    int | None
    created_by:    int | None
    created_at:    datetime | None
    profile_image: str | None = None
    dial_code:     str | None = None
    phone_number:  str | None = None

    @classmethod
    def from_entity(cls, user) -> "UserResponse":
        return cls(
            id=user.id,
            name=user.name,
            last_name=user.last_name,
            email=user.email,
            role_id=user.role_id,
            role_name=user.role_name,
            circuit_id=user.circuit_id,
            created_by=user.created_by,
            created_at=user.created_at,
            profile_image=user.profile_image,
            dial_code=user.dial_code,
            phone_number=user.phone_number,
        )
