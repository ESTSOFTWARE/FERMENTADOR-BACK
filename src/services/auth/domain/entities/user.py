from dataclasses import dataclass

from src.services.auth.domain.entities.role import Role


@dataclass
class User:
    id:         int
    name:       str
    last_name:  str
    email:      str
    role_id:    int
    password:        str | None = None
    circuit_id:      int | None = None
    role:            Role | None = None
    created_by:      int | None = None
    profile_image:   str | None = None
    oauth_google_id: str | None = None
    oauth_github_id: str | None = None
