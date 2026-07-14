import logging

from src.core.groq.recommendation_service import generate_anomaly_recommendation
from src.services.fermentation.infrastructure.adapters.postgres import FermentationRepository
from src.services.notifications.application.usecase.send_notification_use_case import (
    SendNotificationUseCase,
)
from src.services.notifications.infrastructure.adapters.postgres import NotificationRepository

logger = logging.getLogger(__name__)


async def receive_ml_result(
    result: dict,
    fermentation_repo: FermentationRepository,
    notification_repo: NotificationRepository,
) -> None:
    """
    Recibe el resultado del ML service:
    - Si es anomalía: genera recomendación vía Groq, guarda notificación en DB
      y la empuja por WebSocket al usuario dueño del circuito.
    - Si es predicción de eficiencia: solo registra (sin notificación intrusiva).
    """
    result_type = result.get("type")
    circuit_id  = result.get("circuit_id")
    session_id  = result.get("session_id")

    if result_type != "anomaly" or not result.get("is_anomaly"):
        return

    session = await fermentation_repo.get_active_session_by_circuit(circuit_id)
    if session is None:
        logger.warning("[ML] No se encontró sesión activa para circuit_id=%s", circuit_id)
        return

    user_id = session.user_id

    anomaly_score    = result.get("anomaly_score", 0.0)
    sensor_snapshot  = result.get("sensor_snapshot")

    recommendation = generate_anomaly_recommendation(
        anomaly_score=anomaly_score,
        session_id=session_id or session.id,
        sensor_snapshot=sensor_snapshot,
    )

    use_case = SendNotificationUseCase(repository=notification_repo)
    await use_case.execute(
        user_id=user_id,
        message=recommendation,
        notification_type="recommendation",
        session_id=session_id or session.id,
    )

    logger.info(
        "[ML] Recomendación enviada → user_id=%s circuit=%s score=%.3f",
        user_id, circuit_id, anomaly_score,
    )
