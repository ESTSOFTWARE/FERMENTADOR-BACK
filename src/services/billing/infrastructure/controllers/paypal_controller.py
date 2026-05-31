import logging

from fastapi import HTTPException, Request

from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.services.billing.application.usecase.create_paypal_order_use_case import (
    CreatePayPalOrderUseCase,
)
from src.services.billing.application.usecase.create_paypal_subscription_use_case import (
    CreatePayPalSubscriptionUseCase,
)
from src.services.billing.application.usecase.handle_paypal_webhook_use_case import (
    HandlePayPalWebhookUseCase,
)
from src.services.billing.domain.dto.billing_schema import (
    CreatePayPalOrderRequest,
    CreatePayPalSubscriptionRequest,
)
from src.services.billing.infrastructure.adapters.MySQL import BillingRepository
from src.services.billing.infrastructure.adapters.paypal_adapter import PayPalAdapter

logger = logging.getLogger(__name__)


async def create_paypal_subscription(
    body: CreatePayPalSubscriptionRequest,
    current_user: dict,
) -> dict:
    repo   = BillingRepository(AsyncSessionLocal)
    paypal = PayPalAdapter()
    try:
        subscription_id = await CreatePayPalSubscriptionUseCase(repo, paypal).execute(
            user_id=current_user["user_id"],
            plan=body.plan,
            billing_cycle=body.billing_cycle,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"subscription_id": subscription_id}


async def create_paypal_order(
    body: CreatePayPalOrderRequest,
    current_user: dict,
) -> dict:
    paypal = PayPalAdapter()
    try:
        order_id = await CreatePayPalOrderUseCase(paypal).execute(
            amount=body.amount,
            currency=body.currency,
            description=body.description,
        )
    except Exception as exc:
        logger.exception("Error creando orden PayPal")
        raise HTTPException(status_code=500, detail=str(exc))
    return {"order_id": order_id}


async def capture_paypal_order(order_id: str, current_user: dict) -> dict:
    paypal = PayPalAdapter()
    try:
        result = await paypal.capture_order(order_id)
    except Exception as exc:
        logger.exception("Error capturando orden PayPal")
        raise HTTPException(status_code=500, detail=str(exc))
    return result


async def get_paypal_client_token(current_user: dict) -> dict:
    paypal = PayPalAdapter()
    try:
        client_token = await paypal.generate_client_token()
    except Exception as exc:
        logger.exception("Error generando client token PayPal")
        raise HTTPException(status_code=500, detail=str(exc))
    return {"client_token": client_token}


async def handle_paypal_webhook(request: Request) -> dict:
    body = await request.json()

    event_type = body.get("event_type", "")
    resource   = body.get("resource", {})

    repo = BillingRepository(AsyncSessionLocal)
    await HandlePayPalWebhookUseCase(repo).execute(event_type, resource)

    return {"status": "ok"}
