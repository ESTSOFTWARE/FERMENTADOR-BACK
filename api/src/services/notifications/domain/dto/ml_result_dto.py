from pydantic import BaseModel


class MlResultDTO(BaseModel):
    type: str          # "anomaly" | "efficiency"
    session_id: int
    circuit_id: int
    is_anomaly: bool | None = None
    anomaly_score: float | None = None
    detected_at: str | None = None
    predicted_efficiency_percent: float | None = None
    predicted_at: str | None = None