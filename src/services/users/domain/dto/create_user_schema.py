from pydantic import BaseModel, EmailStr, model_validator

from src.core.validators import DialCodeStr, PhoneNumberStr


class CreateUserRequest(BaseModel):
    name:            str
    last_name:       str
    email:           EmailStr
    password:        str
    role:            str
    activation_code: str
    dial_code:       DialCodeStr    = None
    phone_number:    PhoneNumberStr = None

    @model_validator(mode="after")
    def phone_fields_together(self):
        if (self.dial_code is None) != (self.phone_number is None):
            raise ValueError("dial_code y phone_number deben enviarse juntos o ambos omitirse")
        return self
