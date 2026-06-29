from fastapi import APIRouter, Depends, Query, Request

from src.core.dependencies import get_current_user, require_any_role, require_soporte
from src.services.billing.domain.dto.billing_schema import (
    CreateCheckoutRequest,
    CreatePayPalOrderRequest,
    CreatePayPalSubscriptionRequest,
    SubscriptionResponse,
    SupportSubscriptionResponse,
)
from src.services.billing.infrastructure.controllers.checkout_controller import create_checkout
from src.services.billing.infrastructure.controllers.paypal_controller import (
    capture_paypal_order,
    create_paypal_order,
    create_paypal_subscription,
    get_paypal_client_token,
    handle_paypal_webhook,
)
from src.services.billing.infrastructure.controllers.subscription_controller import (
    cancel_subscription,
    get_subscription,
)
from src.services.billing.infrastructure.controllers.support_controller import list_subscriptions
from src.services.billing.infrastructure.controllers.webhook_controller import handle_webhook

router = APIRouter()


@router.post(
    "/checkout",
    summary="Crear sesión de pago en Stripe",
)
async def checkout_route(
    body: CreateCheckoutRequest,
    current_user: dict = Depends(require_any_role),
):
    return await create_checkout(body, current_user)


@router.get(
    "/subscription",
    response_model=SubscriptionResponse | None,
    summary="Obtener suscripción activa del usuario",
)
async def get_subscription_route(
    current_user: dict = Depends(get_current_user),
):
    return await get_subscription(current_user)


@router.get(
    "/entitlements",
    summary="Plan y features habilitadas del usuario (para gatear la UI)",
)
async def get_entitlements_route(
    current_user: dict = Depends(get_current_user),
):
    from src.core.entitlements import get_user_entitlements
    return await get_user_entitlements(current_user["user_id"])


@router.delete(
    "/subscription",
    summary="Cancelar suscripción al final del período",
)
async def cancel_subscription_route(
    current_user: dict = Depends(require_any_role),
):
    return await cancel_subscription(current_user)


@router.post(
    "/webhook",
    summary="Webhook de eventos de Stripe",
    include_in_schema=False,
)
async def webhook_route(request: Request):
    return await handle_webhook(request)


@router.get(
    "/support/subscriptions",
    response_model=list[SupportSubscriptionResponse],
    summary="Panel soporte — listar todas las suscripciones",
)
async def support_subscriptions_route(
    status: str | None = Query(None),
    plan:   str | None = Query(None),
    limit:  int        = Query(50, ge=1, le=200),
    offset: int        = Query(0, ge=0),
    _: dict = Depends(require_soporte),
):
    return await list_subscriptions(status=status, plan=plan, limit=limit, offset=offset)


# ── PayPal ──────────────────────────────────────────────────────────────────

@router.get(
    "/paypal/client-token",
    summary="Generar client token PayPal para Hosted Fields (tarjeta embebida)",
)
async def paypal_client_token_route(
    current_user: dict = Depends(require_any_role),
):
    return await get_paypal_client_token(current_user)


@router.post(
    "/paypal/subscription",
    summary="Iniciar suscripción PayPal — devuelve subscription_id para aprobación",
)
async def paypal_subscription_route(
    body: CreatePayPalSubscriptionRequest,
    current_user: dict = Depends(require_any_role),
):
    return await create_paypal_subscription(body, current_user)


@router.post(
    "/paypal/order",
    summary="Crear orden PayPal para compra única",
)
async def paypal_order_route(
    body: CreatePayPalOrderRequest,
    current_user: dict = Depends(require_any_role),
):
    return await create_paypal_order(body, current_user)


@router.post(
    "/paypal/order/{order_id}/capture",
    summary="Capturar pago de orden PayPal",
)
async def paypal_capture_route(
    order_id: str,
    current_user: dict = Depends(require_any_role),
):
    return await capture_paypal_order(order_id, current_user)


@router.post(
    "/paypal/webhook",
    summary="Webhook de eventos de PayPal",
    include_in_schema=False,
)
async def paypal_webhook_route(request: Request):
    return await handle_paypal_webhook(request)
