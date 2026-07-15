from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id:         int
    name:       str
    last_name:  str
    email:      str
    password:   str
    role_id:    int
    circuit_id:            int | None = None
    circuit_code:          str | None = None
    role_name:             str | None = None
    created_by:            int | None = None
    created_at:            datetime | None = None
    dial_code:             str | None = None
    phone_number:          str | None = None
    description:           str | None = None
    profile_image:         str | None = None
    oauth_google_id:       str | None = None
    oauth_github_id:       str | None = None
    tour_completed:        bool = False
    is_active:             bool = True
    warning_email_sent_at: datetime | None = None
    reactivated_at:        datetime | None = None
    last_oauth_login_at:   datetime | None = None