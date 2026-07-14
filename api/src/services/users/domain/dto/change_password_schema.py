from pydantic import BaseModel, model_validator

from src.core.validators import PasswordStr


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password:     PasswordStr  # 8+ caracteres, con letras y números
    confirm_password: str

    @model_validator(mode="after")
    def validate(self):
        if self.new_password == self.current_password:
            raise ValueError("La nueva contraseña no puede ser igual a la actual")
        if self.new_password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return self
