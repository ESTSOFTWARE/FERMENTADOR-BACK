from pydantic import BaseModel, EmailStr, Field

from src.services.auth.domain.dto.user_schema import UserResponse


class LoginRequest(BaseModel):
    email:    EmailStr
    # En login no exigimos fortaleza (puede ser una contraseña vieja), solo
    # límites razonables para evitar payloads gigantes.
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str
    user:          UserResponse


class LoginCookieResponse(BaseModel):
    user: UserResponse
