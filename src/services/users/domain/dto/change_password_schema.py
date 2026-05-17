from pydantic import BaseModel, model_validator


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password:     str
    confirm_password: str

    @model_validator(mode="after")
    def validate(self):
        if len(self.new_password) < 8:
            raise ValueError("La nueva contraseña debe tener al menos 8 caracteres")
        if self.new_password == self.current_password:
            raise ValueError("La nueva contraseña no puede ser igual a la actual")
        if self.new_password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return self
