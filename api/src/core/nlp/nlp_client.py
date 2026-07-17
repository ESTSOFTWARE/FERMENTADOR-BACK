"""
Puente Backend → NLP service.

Cuando una fermentación termina (completada o interrumpida), el backend
dispara `request_notes_generation()` reenviando el JWT del usuario que la
detuvo. El NLP usa ese mismo token para leer el reporte y guardar la nota
con PATCH /api/fermentation/{session_id}/report/notes.

Fire-and-forget: nunca bloquea la respuesta de /stop e ignora errores
(si el NLP está caído, la fermentación se detiene igual).
"""
import logging

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)

# El NLP llama a un LLM, así que puede tardar; al ser fire-and-forget no afecta
# al usuario.
_TIMEOUT_SECONDS = 60.0


async def request_notes_generation(session_id: int, bearer_token: str) -> None:
    if not settings.NLP_SERVICE_URL:
        logger.info(
            "[NLP] NLP_SERVICE_URL no configurado; se omite la nota — session=%s",
            session_id,
        )
        return

    url = (
        f"{settings.NLP_SERVICE_URL.rstrip('/')}"
        f"/api/v1/sessions/{session_id}/generate-notes"
    )
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {bearer_token}"},
            )
            response.raise_for_status()
        logger.info("[NLP] Nota generada y guardada — session=%s", session_id)
    except Exception:  # noqa: BLE001 — no debe romper el flujo de /stop
        logger.exception("[NLP] No se pudo generar la nota — session=%s", session_id)
