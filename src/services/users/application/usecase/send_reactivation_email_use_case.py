import logging
from datetime import datetime

from src.core.email.email_service import send_reactivation_email
from src.services.users.infrastructure.adapters.postgres import UserRepository

logger = logging.getLogger(__name__)


class SendReactivationEmailUseCase:
    """
    Envía correo de reactivación cuando un usuario reactiva su cuenta mediante OAuth.
    
    Registra:
    - reactivated_at: momento de la reactivación
    - last_oauth_login_at: momento del último login OAuth
    - is_active: TRUE (cuenta reactivada)
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: int, user_name: str, user_email: str) -> bool:
        """
        Envía el correo de reactivación y registra los timestamps.
        
        Args:
            user_id: ID del usuario
            user_name: Nombre del usuario
            user_email: Email del usuario
            
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        try:
            # Enviar correo
            await send_reactivation_email(user_email, user_name)

            # Registrar timestamps de reactivación
            now = datetime.utcnow()
            await self.user_repository.update_reactivation_timestamps(
                user_id=user_id,
                reactivated_at=now,
                last_oauth_login_at=now,
            )

            logger.info(f"[Reactivation Email] Usuario {user_id} reactivado y correo enviado a {user_email}")
            return True

        except Exception as e:
            logger.error(f"[Reactivation Email] Error al reactivar usuario {user_id}: {e}")
            return False
