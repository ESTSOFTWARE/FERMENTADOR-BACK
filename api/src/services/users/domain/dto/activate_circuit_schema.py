from pydantic import BaseModel


class ActivateCircuitRequest(BaseModel):
    activation_code: str


class ActivateCircuitResponse(BaseModel):
    access_token: str
    token_type:   str
    circuit_id:   int
