from pydantic import BaseModel


class GoogleMobileRequest(BaseModel):
    id_token: str
