from pydantic import BaseModel, field_validator


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email:        str
    code:         str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class MessageResponse(BaseModel):
    message: str
