from pydantic import BaseModel


class ActivateCircuitRequest(BaseModel):
    activation_code: str
