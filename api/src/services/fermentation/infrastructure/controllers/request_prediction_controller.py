import logging
from datetime import datetime, timedelta, timezone

import httpx

from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.core.groq.recommendation_service import generate_efficiency_recommendation
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository
from src.services.notifications.application.usecase.send_notification_use_case import (
    SendNotificationUseCase,
)
from src.services.notifications.infrastructure.adapters.postgres import NotificationRepository
from src.services.sensors.infrastructure.adapters.postgres import SensorRepository

logger = logging.getLogger(__name__)

HISTORY_HOURS = 2
_SENSOR_KEYS = ["ph", "temperature", "turbidity", "conductivity", "alcohol"]


class PredictionResult:
    def __init__(self, efficiency: float, message: str):
        self.efficiency = efficiency
        self.message = message


async def request_prediction(session_id: int) -> PredictionResult | None:
    ferm_repo    = FermentationRepository(AsyncSessionLocal)
    sensor_repo  = SensorRepository(AsyncSessionLocal)

    session = await ferm_repo.get_session_by_id(session_id)
    if session is None:
        raise ValueError(f"Sesión {session_id} no encontrada.")

    circuit_id = session.circuit_id
    now        = datetime.now(timezone.utc)
    from_dt    = (now - timedelta(hours=HISTORY_HOURS)).replace(tzinfo=None)
    origin     = (session.actual_start or session.scheduled_start)
    if hasattr(origin, "tzinfo") and origin.tzinfo:
        origin = origin.replace(tzinfo=None)

    # Historial de temperatura como eje temporal.
    # Se filtra solo por circuit_id + from_dt porque el hardware envía
    # session_id=null en los mensajes MQTT, por lo que los readings
    # quedan en BD sin session_id y el filtro por id devolvería 0 filas.
    temp_readings = await sensor_repo.get_history(
        circuit_id, "temperature", from_dt=from_dt
    )
    logger.info("[ML] Historial temperatura → circuit=%s from_dt=%s count=%s", circuit_id, from_dt, len(temp_readings))
    if len(temp_readings) < 2:
        logger.warning("[ML] Historial insuficiente para predicción — session=%s", session_id)
        return None

    # Historial del resto de sensores
    other_history: dict[str, list] = {}
    for stype in _SENSOR_KEYS:
        if stype == "temperature":
            continue
        other_history[stype] = await sensor_repo.get_history(
            circuit_id, stype, from_dt=from_dt
        )

    # Construir series de tiempo alineadas
    time_hours: list[float]       = []
    ph_vals: list[float]          = []
    temp_vals: list[float]        = []
    turbidity_vals: list[float]   = []
    conductivity_vals: list[float] = []
    alcohol_vals: list[float]     = []

    for temp_r in temp_readings:
        ts = temp_r.timestamp
        snap: dict[str, float] = {"temperature": float(temp_r.value)}

        for stype, readings in other_history.items():
            closest = None
            for r in readings:
                if r.timestamp <= ts:
                    closest = r
                else:
                    break
            snap[stype] = float(closest.value) if closest else 0.0

        elapsed = (ts - origin).total_seconds() / 3600
        time_hours.append(round(elapsed, 4))
        temp_vals.append(snap["temperature"])
        ph_vals.append(snap.get("ph", 0.0))
        turbidity_vals.append(snap.get("turbidity", 0.0))
        conductivity_vals.append(snap.get("conductivity", 0.0))
        alcohol_vals.append(snap.get("alcohol", 0.0))

    payload = {
        "time_hours":       time_hours,
        "ph":               ph_vals,
        "temperature_c":    temp_vals,
        "turbidity":        turbidity_vals,
        "conductivity":     conductivity_vals,
        "alcohol_percent":  alcohol_vals,
    }

    ml_url = f"{settings.ML_SERVICE_URL.rstrip('/')}/api/v1/predict/efficiency"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(ml_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        logger.error("[ML] Error llamando a %s: %s", ml_url, exc)
        return None

    efficiency = data.get("efficiency_percent")
    if efficiency is None:
        logger.error("[ML] Respuesta sin efficiency_percent: %s", data)
        return None

    logger.info("[ML] Predicción → session=%s efficiency=%.1f%%", session_id, efficiency)

    message = generate_efficiency_recommendation(
        efficiency_percent=efficiency,
        session_id=session_id,
    )

    # Solo BD (historial campanita). Sin WS ni FCM: el resultado lo recibe
    # únicamente quien lo pidió en la respuesta HTTP, y esa plataforma genera
    # su propia notificación local (móvil → notificación local, web → browser).
    try:
        notif_repo = NotificationRepository(AsyncSessionLocal)
        await SendNotificationUseCase(notif_repo).execute(
            user_id=session.user_id,
            message=message,
            notification_type="efficiency",
            session_id=session_id,
            push=False,
            broadcast=False,
        )
    except Exception:  # noqa: BLE001
        logger.warning("[ML] No se pudo enviar notificación — session=%s", session_id)

    return PredictionResult(efficiency=efficiency, message=message)
