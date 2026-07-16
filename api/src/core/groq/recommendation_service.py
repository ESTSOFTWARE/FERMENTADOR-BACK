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

_SYSTEM_EFFICIENCY = (
    "Eres un experto en fermentación de café de especialidad. "
    "Genera UNA observación breve y accionable (máx. 20 palabras) "
    "sobre la eficiencia predicha de la fermentación. "
    "Responde SOLO la observación, sin prefijos, listas ni explicaciones."
)

_SYSTEM_NOTES = (
    "Eres un experto en fermentación de café de especialidad. "
    "Redacta un análisis técnico conciso (4-6 oraciones) del proceso de fermentación "
    "basado en los datos del reporte. Incluye observaciones sobre la eficiencia, "
    "el comportamiento de los sensores y recomendaciones para futuras fermentaciones. "
    "Responde ÚNICAMENTE el análisis en español, sin encabezados, listas ni bullets."
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


def generate_efficiency_recommendation(
    efficiency_percent: float,
    session_id: int,
) -> str:
    fallback = f"Eficiencia estimada: {efficiency_percent:.1f}%."
    if not settings.GROQ_API_KEY:
        return fallback
    try:
        response = _client_instance().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": _SYSTEM_EFFICIENCY},
                {
                    "role": "user",
                    "content": f"Sesión {session_id}. Eficiencia predicha: {efficiency_percent:.1f}%.",
                },
            ],
            temperature=0.4,
            max_tokens=60,
        )
        text = response.choices[0].message.content.strip()
        return text or fallback
    except Exception:
        logger.exception("[Groq] Error generando recomendación de eficiencia")
        return fallback


def generate_report_notes(report, session_id: int) -> str:
    fallback = (
        f"Fermentación F-{session_id:03d} finalizada con estado "
        f"'{report.session_status or 'desconocido'}'. "
        f"Eficiencia registrada: {f'{report.efficiency:.1f}%' if report.efficiency is not None else 'no disponible'}."
    )
    if not settings.GROQ_API_KEY:
        return fallback

    def _fmt(v, suffix=""):
        return f"{v:.2f}{suffix}" if v is not None else "N/A"

    context = (
        f"Estado: {report.session_status or 'desconocido'}. "
        f"Eficiencia: {_fmt(report.efficiency, '%')}. "
        f"Azúcar inicial: {_fmt(report.initial_sugar, ' g/L')}. "
        f"Etanol detectado: {_fmt(report.ethanol_detected, '%')}. "
        f"Etanol teórico: {_fmt(report.theoretical_ethanol, '%')}. "
        f"Temperatura: inicial {_fmt(report.temperature_initial, '°C')}, final {_fmt(report.temperature_final, '°C')}. "
        f"pH: inicial {_fmt(report.ph_initial)}, final {_fmt(report.ph_final)}. "
        f"Alcohol: inicial {_fmt(report.alcohol_initial, '%')}, final {_fmt(report.alcohol_final, '%')}. "
        f"Conductividad: inicial {_fmt(report.conductivity_initial, ' mS/cm')}, final {_fmt(report.conductivity_final, ' mS/cm')}. "
        f"Turbidez: inicial {_fmt(report.turbidity_initial)}, final {_fmt(report.turbidity_final)}."
    )

    try:
        response = _client_instance().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": _SYSTEM_NOTES},
                {"role": "user", "content": f"Sesión {session_id}. {context}"},
            ],
            temperature=0.5,
            max_tokens=300,
        )
        text = response.choices[0].message.content.strip()
        return text or fallback
    except Exception:
        logger.exception("[Groq] Error generando notas del reporte")
        return fallback


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
