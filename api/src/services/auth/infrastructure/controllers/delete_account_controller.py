from src.core.email.email_service import send_account_deletion_request
from src.services.auth.domain.dto.delete_account_schema import DeleteAccountRequest


async def request_account_deletion(body: DeleteAccountRequest) -> dict:
    await send_account_deletion_request(body.name, body.email, body.reason)
    return {
        "message": "Solicitud recibida. Tu cuenta se eliminará en un plazo de 72 horas.",
    }
