import logging

import stripe

from src.core.config import settings

logger = logging.getLogger(__name__)

PRICE_MAP: dict[str, dict[str, str]] = {
    "starter":    {"monthly": settings.STRIPE_PRICE_STARTER_MONTHLY,    "annual": settings.STRIPE_PRICE_STARTER_ANNUAL},
    "academic":   {"monthly": settings.STRIPE_PRICE_ACADEMIC_MONTHLY,   "annual": settings.STRIPE_PRICE_ACADEMIC_ANNUAL},
    "enterprise": {"monthly": settings.STRIPE_PRICE_ENTERPRISE_MONTHLY, "annual": settings.STRIPE_PRICE_ENTERPRISE_ANNUAL},
}


class StripeAdapter:

    def __init__(self) -> None:
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_customer(self, email: str, name: str) -> str:
        customer = stripe.Customer.create(email=email, name=name)
        return customer.id

    def get_price_id(self, plan: str, billing_cycle: str) -> str:
        price_id = PRICE_MAP.get(plan, {}).get(billing_cycle, "")
        if not price_id:
            raise ValueError(f"Price ID no configurado para {plan}/{billing_cycle}")
        return price_id

    def create_checkout_session(
        self,
        customer_id: str,
        price_id:    str,
        user_id:     int,
        return_url:  str,
    ) -> str:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            ui_mode="embedded",
            return_url=return_url,
            metadata={"user_id": str(user_id)},
            subscription_data={
                "metadata": {"user_id": str(user_id)},
            },
        )
        return session.client_secret

    def cancel_subscription(self, stripe_subscription_id: str) -> None:
        stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True,
        )

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> stripe.Event:
        return stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
