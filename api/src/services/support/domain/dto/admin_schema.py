from datetime import datetime

from pydantic import BaseModel


class RoleSchema(BaseModel):
    id: int
    name: str

class CircuitSchema(BaseModel):
    id: int | None
    code: str | None
    has_circuit: bool

class PhoneSchema(BaseModel):
    dial_code: str | None
    number: str | None

class AdminResponse(BaseModel):
    id: int
    name: str
    last_name: str
    email: str
    role: RoleSchema
    circuit: CircuitSchema
    auth_provider: str
    profile_image: str | None
    phone: PhoneSchema
    created_at: datetime | None

    @classmethod
    def from_entity(cls, user) -> "AdminResponse":
        auth_provider = "email"
        if user.oauth_google_id:
            auth_provider = "google"
        elif user.oauth_github_id:
            auth_provider = "github"

        role_id = user.role.id if user.role else user.role_id
        role_name = user.role.name if user.role else "admin"

        return cls(
            id=user.id,
            name=user.name,
            last_name=user.last_name,
            email=user.email,
            role=RoleSchema(
                id=role_id,
                name=role_name
            ),
            circuit=CircuitSchema(
                id=user.circuit_id,
                code=user.circuit.activation_code if user.circuit else None,
                has_circuit=user.circuit_id is not None
            ),
            auth_provider=auth_provider,
            profile_image=user.profile_image,
            phone=PhoneSchema(
                dial_code=user.dial_code,
                number=user.phone_number
            ),
            created_at=user.created_at,
        )
