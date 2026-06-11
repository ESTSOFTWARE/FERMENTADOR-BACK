from pydantic import BaseModel


class StopFermentationRequest(BaseModel):
    interrupted: bool = False
