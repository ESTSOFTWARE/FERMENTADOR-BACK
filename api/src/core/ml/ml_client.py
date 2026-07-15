"""
Puente Backend → ML service.

Después de guardar una lectura de sensor, el SensorThread llama
`forward_reading()`. Si ya hay datos de los 5 sensores requeridos
y no se llamó al ML en los últimos COOLDOWN_SECONDS, arma el
RealtimeReadingDTO y hace POST al ML service.

Fire-and-forget: nunca bloquea el hilo principal, ignora errores.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)

REQUIRED = {"ph", "temperature", "turbidity", "conductivity", "alcohol"}
HISTORY_HOURS  = 2
COOLDOWN_SECONDS = 60
_TIMEOUT = 5.0

# circuit_id → último timestamp en que se llamó al ML
_last_call: dict[int, datetime] = {}


async def forward_reading(
    circuit_id:   int,
    session_id:   int,
    actual_start: datetime,
    scheduled_start: datetime,
    scheduled_end:   datetime,
    sensor_repo,        # SensorRepository — inyectado desde SensorThread
    force: bool = False,
) -> None:
    if not settings.ML_SERVICE_URL:
        return

    now = datetime.now(timezone.utc)

    # Cooldown por circuito (omitido si force=True)
    last = _last_call.get(circuit_id)
    if not force and last and (now - last).total_seconds() < COOLDOWN_SECONDS:
        return

    try:
        # ── 1. Lecturas actuales ──────────────────────────────────────────
        latest: dict[str, Any] = {}
        for stype in REQUIRED:
            r = await sensor_repo.get_latest_reading(circuit_id, stype)
            if r:
                latest[stype] = r

        if len(latest) < len(REQUIRED):
            return  # faltan sensores, esperar a que todos reporten

        current = _snapshot(latest)

        # ── 2. Historial de las últimas HISTORY_HOURS ─────────────────────
        from_dt = now - timedelta(hours=HISTORY_HOURS)

        # Usar temperatura como espina temporal
        temp_readings = await sensor_repo.get_history(
            circuit_id, "temperature", session_id=session_id, from_dt=_naive(from_dt)
        )

        # Historial del resto de sensores (lista ordenada asc por timestamp)
        other: dict[str, list] = {}
        for stype in REQUIRED - {"temperature"}:
            other[stype] = await sensor_repo.get_history(
                circuit_id, stype, session_id=session_id, from_dt=_naive(from_dt)
            )

        # Construir snapshots: por cada lectura de temperatura, busca el
        # último valor conocido de cada otro sensor en ese instante.
        history_snapshots = []
        history_hours_list = []
        origin = (actual_start or scheduled_start).replace(tzinfo=None)

        for temp_r in temp_readings:
            snap: dict[str, Any] = {"temperature": temp_r}
            ts = temp_r.timestamp

            for stype, readings in other.items():
                closest = None
                for r in readings:
                    if r.timestamp <= ts:
                        closest = r
                    else:
                        break
                if closest:
                    snap[stype] = closest

            if len(snap) == len(REQUIRED):
                history_snapshots.append(_snapshot(snap))
                elapsed = (ts - origin).total_seconds() / 3600
                history_hours_list.append(round(elapsed, 4))

        # ── 3. Tiempos ────────────────────────────────────────────────────
        origin_aware = (actual_start or scheduled_start)
        if origin_aware.tzinfo is None:
            origin_aware = origin_aware.replace(tzinfo=timezone.utc)

        elapsed_hours = max((now - origin_aware).total_seconds() / 3600, 0.0)
        planned_hours = (scheduled_end - scheduled_start).total_seconds() / 3600
        if planned_hours <= 0:
            planned_hours = 48.0

        payload = {
            "session_id":            session_id,
            "circuit_id":            circuit_id,
            "timestamp":             now.isoformat(),
            "current":               current,
            "history_hours":         history_hours_list,
            "history":               history_snapshots,
            "elapsed_hours":         round(elapsed_hours, 4),
            "planned_duration_hours": round(planned_hours, 4),
        }

        _last_call[circuit_id] = now

        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.ML_SERVICE_URL.rstrip('/')}/api/v1/realtime/reading",
                json=payload,
            )
            resp.raise_for_status()

        logger.info(
            "[ML] Lectura enviada → circuit=%s session=%s elapsed=%.2fh",
            circuit_id, session_id, elapsed_hours,
        )

    except Exception:
        logger.exception("[ML] Error enviando lectura al ML service (circuit=%s)", circuit_id)


def _snapshot(readings: dict) -> dict:
    def v(key: str) -> float:
        r = readings.get(key)
        return float(r.value) if r else 0.0

    return {
        "ph":              v("ph"),
        "temperature_c":   v("temperature"),
        "turbidity":       v("turbidity"),
        "conductivity":    v("conductivity"),
        "alcohol_percent": v("alcohol"),
    }


def _naive(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None) if dt.tzinfo else dt
