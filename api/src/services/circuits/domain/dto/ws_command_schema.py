from pydantic import BaseModel


class WSCommandRequest(BaseModel):
    command:    str
    parameters: dict = {}
