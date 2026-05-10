from pydantic import BaseModel, EmailStr

from src.services.auth.domain.dto.user_schema import UserResponse


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str
    user:          UserResponse
