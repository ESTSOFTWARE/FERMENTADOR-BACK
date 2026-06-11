import logging
from datetime import datetime, timedelta

from src.core.database import AsyncSessionLocal
from src.core.email.email_service import send_warning_email
from src.services.users.infrastructure.adapters.postgres import UserRepository

logger = logging.getLogger(__name__)


class SendWarningEmailUseCase:
    """
    Envía correo de advertencia a usuarios cuyas cuentas vencen en 2 días.
    
    Condiciones:
    - is_active = TRUE
    - circuit_id = NULL
    - created_at hace exactamente 28 días (2 días antes del vencimiento de 30 días)
    - warning_email_sent_at = NULL (no se ha enviado aún)
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self) -> int:
        """
        Busca usuarios que deben recibir el correo de advertencia y lo envía.
        
        Returns:
            int: Número de correos enviados
        """
        count = 0
        try:
            # Calcular fecha límite: hace 28 días
            now = datetime.utcnow()
            twenty_eight_days_ago = now - timedelta(days=28)

            # Obtener usuarios que cumplen las condiciones
            users = await self.user_repository.get_users_for_warning_email(
                created_before=twenty_eight_days_ago
            )

            for user in users:
                try:
                    # Enviar correo
                    await send_warning_email(user.email, user.name)

                    # Registrar que se envió el correo
                    await self.user_repository.update_warning_email_sent(user.id)
                    count += 1
                    logger.info(f"[Warning Email] Correo enviado a {user.email}")

                except Exception as e:
                    logger.error(f"[Warning Email] Error al enviar a {user.email}: {e}")
                    # Continuar con el siguiente usuario

            if count > 0:
                logger.info(f"[Warning Email] {count} correo(s) de advertencia enviado(s)")

        except Exception as e:
            logger.error(f"[Warning Email] Error en tarea de envío: {e}")

        return count
