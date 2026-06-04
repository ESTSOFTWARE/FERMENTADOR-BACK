import logging

import stripe
from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.database import AsyncSessionLocal
from src.services.billing.application.usecase.handle_webhook_use_case import HandleWebhookUseCase
from src.services.billing.infrastructure.adapters.postgres import BillingRepository
from src.services.billing.infrastructure.adapters.stripe_adapter import StripeAdapter

logger = logging.getLogger(__name__)


async def handle_webhook(request: Request) -> JSONResponse:
    payload    = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        repo   = BillingRepository(AsyncSessionLocal)
        stripe_adapter = StripeAdapter()
        await HandleWebhookUseCase(repo, stripe_adapter).execute(payload, sig_header)
        return JSONResponse({"received": True})
    except stripe.SignatureVerificationError:
        logger.warning("[Webhook] Firma de Stripe inválida")
        return JSONResponse({"error": "Invalid signature"}, status_code=400)
    except Exception as e:
        logger.error(f"[Webhook] Error procesando evento: {e}")
        return JSONResponse({"error": "Internal error"}, status_code=500)
