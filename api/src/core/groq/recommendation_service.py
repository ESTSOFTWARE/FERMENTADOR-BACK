import logging

from groq import Groq

from src.core.config import settings

logger = logging.getLogger(__name__)

_client: Groq | None = None

_FALLBACK = "Anomalía detectada. Verifica los parámetros de fermentación."

_SYSTEM = (
    "Eres un experto en fermentación de café de especialidad. "
    "Genera UNA recomendación breve y accionable (máx. 20 palabras) "
    "para el operador, basada en los datos de la anomalía detectada. "
    "Responde SOLO la recomendación, sin prefijos, listas ni explicaciones."
)


def _client_instance() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def _sensor_context(snapshot: dict) -> str:
    parts = []
    mapping = [
        ("ph",              "pH",             ".2f"),
        ("temperature_c",   "temperatura",    ".1f°C"),
        ("alcohol_percent", "alcohol",        ".1f%v/v"),
        ("turbidity",       "turbidez",       ".1f"),
        ("conductivity",    "conductividad",  ".2f mS/cm"),
    ]
    for key, label, fmt in mapping:
        val = snapshot.get(key)
        if val is not None:
            parts.append(f"{label} {val:{fmt.lstrip('.')}}")
    return ", ".join(parts)


def generate_anomaly_recommendation(
    anomaly_score: float,
    session_id: int,
    sensor_snapshot: dict | None = None,
) -> str:
    if not settings.GROQ_API_KEY:
        return _FALLBACK

    context = f"Score de anomalía: {anomaly_score:.3f}"
    if sensor_snapshot:
        sensors = _sensor_context(sensor_snapshot)
        if sensors:
            context += f" | Sensores: {sensors}"

    try:
        response = _client_instance().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": f"Sesión {session_id}. {context}."},
            ],
            temperature=0.4,
            max_tokens=60,
        )
        text = response.choices[0].message.content.strip()
        return text or _FALLBACK
    except Exception:
        logger.exception("[Groq] Error generando recomendación de anomalía")
        return _FALLBACK
