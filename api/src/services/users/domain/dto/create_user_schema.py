from pydantic import BaseModel, Field, model_validator

from src.core.validators import (
    DialCodeStr,
    NameStr,
    NormalizedEmailStr,
    PasswordStr,
    PhoneNumberStr,
)


class CreateUserRequest(BaseModel):
    name:            NameStr
    last_name:       NameStr
    email:           NormalizedEmailStr
    password:        PasswordStr
    role:            str
    activation_code: str = Field(min_length=1, max_length=64)
    dial_code:       DialCodeStr    = None
    phone_number:    PhoneNumberStr = None

    @model_validator(mode="after")
    def phone_fields_together(self):
        if (self.dial_code is None) != (self.phone_number is None):
            raise ValueError("dial_code y phone_number deben enviarse juntos o ambos omitirse")
        return self
