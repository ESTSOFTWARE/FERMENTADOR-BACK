import logging

from src.core.groq.recommendation_service import (
    generate_anomaly_recommendation,
    generate_efficiency_recommendation,
)
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
    result_type = result.get("type")
    circuit_id  = result.get("circuit_id")
    session_id  = result.get("session_id")

    session = await fermentation_repo.get_active_session_by_circuit(circuit_id)
    if session is None:
        logger.warning("[ML] No se encontró sesión activa para circuit_id=%s", circuit_id)
        return

    use_case = SendNotificationUseCase(repository=notification_repo)
    sid = session_id or session.id

    if result_type == "anomaly" and result.get("is_anomaly"):
        anomaly_score   = result.get("anomaly_score", 0.0)
        sensor_snapshot = result.get("sensor_snapshot")

        message = generate_anomaly_recommendation(
            anomaly_score=anomaly_score,
            session_id=sid,
            sensor_snapshot=sensor_snapshot,
        )
        await use_case.execute(
            user_id=session.user_id,
            message=message,
            notification_type="anomaly",
            session_id=sid,
        )
        logger.info(
            "[ML] Anomalía → user_id=%s circuit=%s score=%.3f",
            session.user_id, circuit_id, anomaly_score,
        )

    elif result_type == "efficiency":
        efficiency = result.get("predicted_efficiency_percent")
        if efficiency is None:
            return

        message = generate_efficiency_recommendation(
            efficiency_percent=efficiency,
            session_id=sid,
        )
        await use_case.execute(
            user_id=session.user_id,
            message=message,
            notification_type="efficiency",
            session_id=sid,
        )
        logger.info(
            "[ML] Eficiencia → user_id=%s circuit=%s pct=%.1f%%",
            session.user_id, circuit_id, efficiency,
        )
