from pydantic import BaseModel


class UserResponse(BaseModel):
    id:             int
    name:           str
    last_name:      str
    email:          str
    role:           str
    profile_image:  str | None = None
    oauth_provider: str = 'email'
