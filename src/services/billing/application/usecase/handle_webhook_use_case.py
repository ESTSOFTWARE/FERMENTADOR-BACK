import logging
from datetime import datetime, timezone

import stripe

from src.core.subscription_cache import subscription_cache
from src.services.billing.domain.repository import IBillingRepository
from src.services.billing.infrastructure.adapters.stripe_adapter import StripeAdapter

logger = logging.getLogger(__name__)

PLAN_BY_PRICE: dict[str, tuple[str, str]] = {}


def _parse_period_end(obj: dict) -> datetime | None:
    ts = (
        obj.get("current_period_end")
        or obj.get("billing_cycle_anchor")
    )
    if not ts:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None)


def _build_price_map() -> None:
    from src.core.config import settings
    global PLAN_BY_PRICE
    PLAN_BY_PRICE = {
        settings.STRIPE_PRICE_STARTER_MONTHLY:    ("starter",    "monthly"),
        settings.STRIPE_PRICE_STARTER_ANNUAL:     ("starter",    "annual"),
        settings.STRIPE_PRICE_ACADEMIC_MONTHLY:   ("academic",   "monthly"),
        settings.STRIPE_PRICE_ACADEMIC_ANNUAL:    ("academic",   "annual"),
        settings.STRIPE_PRICE_ENTERPRISE_MONTHLY: ("enterprise", "monthly"),
        settings.STRIPE_PRICE_ENTERPRISE_ANNUAL:  ("enterprise", "annual"),
    }


class HandleWebhookUseCase:

    def __init__(self, repository: IBillingRepository, stripe_adapter: StripeAdapter):
        self._repo   = repository
        self._stripe = stripe_adapter

    async def execute(self, payload: bytes, sig_header: str) -> None:
        if not PLAN_BY_PRICE:
            _build_price_map()

        try:
            event = self._stripe.construct_webhook_event(payload, sig_header)
        except stripe.SignatureVerificationError:
            logger.warning("[Webhook] Firma inválida")
            raise

        event_type = event["type"]
        data       = event["data"]["object"]

        if event_type == "checkout.session.completed":
            await self._on_checkout_completed(data)

        elif event_type in ("customer.subscription.updated", "customer.subscription.created"):
            await self._on_subscription_updated(data)

        elif event_type == "customer.subscription.deleted":
            await self._on_subscription_deleted(data)

        elif event_type == "invoice.payment_failed":
            await self._on_payment_failed(data)

        elif event_type == "invoice.paid":
            await self._on_invoice_paid(data)

    async def _on_checkout_completed(self, session: dict) -> None:
        sub_id      = session.get("subscription")
        customer_id = session.get("customer")
        if not sub_id or not customer_id:
            return

        stripe_sub  = stripe.Subscription.retrieve(sub_id)
        price_id    = stripe_sub["items"]["data"][0]["price"]["id"]
        plan, cycle = PLAN_BY_PRICE.get(price_id, ("starter", "monthly"))
        period_end  = _parse_period_end(dict(stripe_sub))

        subscription = await self._repo.get_by_stripe_customer_id(customer_id)
        if subscription:
            await self._repo.update(
                user_id=subscription.user_id,
                stripe_subscription_id=sub_id,
                plan=plan,
                billing_cycle=cycle,
                status="active",
                current_period_end=period_end,
                cancel_at_period_end=False,
            )
            subscription_cache.invalidate(subscription.user_id)
            logger.info(f"[Webhook] Suscripción activada para customer {customer_id} — {plan}/{cycle}")

    async def _on_subscription_updated(self, sub: dict) -> None:
        sub_id      = sub["id"]
        customer_id = sub["customer"]
        status      = sub["status"]
        period_end  = _parse_period_end(sub)
        cancel_end  = sub.get("cancel_at_period_end", False)
        price_id    = sub["items"]["data"][0]["price"]["id"]
        plan, cycle = PLAN_BY_PRICE.get(price_id, ("starter", "monthly"))

        normalized = "active" if status == "active" else (
            "past_due" if status == "past_due" else "incomplete"
        )

        subscription = await self._repo.get_by_stripe_customer_id(customer_id)
        if subscription:
            await self._repo.update(
                user_id=subscription.user_id,
                stripe_subscription_id=sub_id,
                plan=plan,
                billing_cycle=cycle,
                status=normalized,
                current_period_end=period_end,
                cancel_at_period_end=cancel_end,
            )
            subscription_cache.invalidate(subscription.user_id)

    async def _on_subscription_deleted(self, sub: dict) -> None:
        customer_id = sub["customer"]
        subscription = await self._repo.get_by_stripe_customer_id(customer_id)
        if subscription:
            await self._repo.update(
                user_id=subscription.user_id,
                status="canceled",
                cancel_at_period_end=False,
            )
            subscription_cache.invalidate(subscription.user_id)
            logger.info(f"[Webhook] Suscripción cancelada para customer {customer_id}")

    async def _on_payment_failed(self, invoice: dict) -> None:
        customer_id  = invoice.get("customer")
        subscription = await self._repo.get_by_stripe_customer_id(customer_id)
        if subscription:
            await self._repo.update(user_id=subscription.user_id, status="past_due")
            subscription_cache.invalidate(subscription.user_id)
            logger.warning(f"[Webhook] Pago fallido para customer {customer_id}")

    async def _on_invoice_paid(self, invoice: dict) -> None:
        customer_id  = invoice.get("customer")
        subscription = await self._repo.get_by_stripe_customer_id(customer_id)
        if subscription and subscription.status == "past_due":
            await self._repo.update(user_id=subscription.user_id, status="active")
            subscription_cache.invalidate(subscription.user_id)
            logger.info(f"[Webhook] Pago recuperado para customer {customer_id}")
