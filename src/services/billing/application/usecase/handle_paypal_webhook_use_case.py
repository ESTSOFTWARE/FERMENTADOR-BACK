import logging

from src.services.billing.domain.repository import IBillingRepository

logger = logging.getLogger(__name__)


class HandlePayPalWebhookUseCase:

    def __init__(self, repository: IBillingRepository):
        self._repo = repository

    async def execute(self, event_type: str, resource: dict) -> None:

        if event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
            await self._on_activated(resource)

        elif event_type in ("BILLING.SUBSCRIPTION.CANCELLED",
                            "BILLING.SUBSCRIPTION.EXPIRED"):
            await self._on_cancelled(resource)

        elif event_type == "BILLING.SUBSCRIPTION.PAYMENT.FAILED":
            await self._on_payment_failed(resource)

        elif event_type == "PAYMENT.SALE.COMPLETED":
            await self._on_payment_completed(resource)

    async def _on_activated(self, resource: dict) -> None:
        sub_id = resource.get("id")
        if not sub_id:
            return
        subscription = await self._repo.get_by_paypal_subscription_id(sub_id)
        if subscription:
            await self._repo.update(
                user_id=subscription.user_id,
                status="active",
            )
            logger.info(f"[PayPal Webhook] Suscripción activada: {sub_id}")

    async def _on_cancelled(self, resource: dict) -> None:
        sub_id = resource.get("id")
        if not sub_id:
            return
        subscription = await self._repo.get_by_paypal_subscription_id(sub_id)
        if subscription:
            await self._repo.update(
                user_id=subscription.user_id,
                status="canceled",
            )
            logger.info(f"[PayPal Webhook] Suscripción cancelada: {sub_id}")

    async def _on_payment_failed(self, resource: dict) -> None:
        sub_id = resource.get("id")
        if not sub_id:
            return
        subscription = await self._repo.get_by_paypal_subscription_id(sub_id)
        if subscription:
            await self._repo.update(
                user_id=subscription.user_id,
                status="past_due",
            )
            logger.warning(f"[PayPal Webhook] Pago fallido: {sub_id}")

    async def _on_payment_completed(self, resource: dict) -> None:
        billing_agreement = resource.get("billing_agreement_id")
        if not billing_agreement:
            return
        subscription = await self._repo.get_by_paypal_subscription_id(billing_agreement)
        if subscription and subscription.status == "past_due":
            await self._repo.update(
                user_id=subscription.user_id,
                status="active",
            )
            logger.info(f"[PayPal Webhook] Pago recuperado: {billing_agreement}")
