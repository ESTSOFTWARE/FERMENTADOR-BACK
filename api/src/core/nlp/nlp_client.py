"""
Puente Backend → NLP service.

Cuando una fermentación termina (completada o interrumpida), el backend le
manda el reporte ya calculado al NLP y éste sólo devuelve el texto de la
nota; guardarla es cosa del backend.

Se hace así, y no con el webhook /sessions/{id}/generate-notes, porque ese
exige el JWT del usuario para leer el reporte y escribir la nota de vuelta.
El auto-stop del scheduler no tiene ningún usuario detrás (y los tokens
están atados a la sesión activa, ver core/dependencies.py), así que por esa
vía las fermentaciones que expiran solas nunca tendrían nota.
"""
import logging

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)

# El NLP redacta con un LLM (Groq), así que puede tardar; al llamarse
# fire-and-forget no retrasa la respuesta de /stop.
_TIMEOUT_SECONDS = 60.0


async def generate_notes(report: dict) -> str | None:
    """Devuelve el texto de la nota, o None si el NLP no está configurado
    o falló: la nota es un extra y nunca debe tumbar el cierre de una
    fermentación.
    """
    session_id = report.get("session_id")
    if not settings.NLP_SERVICE_URL:
        logger.info(
            "[NLP] NLP_SERVICE_URL no configurado; se omite la nota — session=%s",
            session_id,
        )
        return None

    url = f"{settings.NLP_SERVICE_URL.rstrip('/')}/api/v1/notes/preview"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            response = await client.post(url, json=report)
            response.raise_for_status()
        return response.json().get("notes") or None
    except Exception:  # noqa: BLE001 — no debe romper el flujo de /stop
        logger.exception("[NLP] No se pudo generar la nota — session=%s", session_id)
        return None
