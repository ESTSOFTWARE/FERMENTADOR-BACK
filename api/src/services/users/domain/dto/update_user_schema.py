from pydantic import BaseModel, EmailStr, model_validator

from src.core.validators import (
    DialCodeStr,
    OptionalNameStr,
    OptionalPasswordStr,
    PhoneNumberStr,
)


class UpdateUserRequest(BaseModel):
    name:          OptionalNameStr = None
    last_name:     OptionalNameStr = None
    email:         EmailStr | None = None
    password:      OptionalPasswordStr = None
    role:          str | None = None
    profile_image: str | None = None
    dial_code:     DialCodeStr    = None
    phone_number:  PhoneNumberStr = None

    @model_validator(mode="after")
    def phone_fields_together(self):
        if (self.dial_code is None) != (self.phone_number is None):
            raise ValueError("dial_code y phone_number deben enviarse juntos o ambos omitirse")
        return self
