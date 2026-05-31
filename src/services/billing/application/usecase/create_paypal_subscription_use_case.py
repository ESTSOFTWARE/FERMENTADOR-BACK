import logging

from src.core.config import settings
from src.services.billing.domain.repository import IBillingRepository
from src.services.billing.infrastructure.adapters.paypal_adapter import PayPalAdapter

logger = logging.getLogger(__name__)

VALID_PLANS  = {"starter", "academic", "enterprise"}
VALID_CYCLES = {"monthly", "annual"}


class CreatePayPalSubscriptionUseCase:

    def __init__(self, repository: IBillingRepository, paypal: PayPalAdapter):
        self._repo   = repository
        self._paypal = paypal

    async def execute(
        self,
        user_id:       int,
        plan:          str,
        billing_cycle: str,
    ) -> str:
        if plan not in VALID_PLANS:
            raise ValueError(f"Plan inválido: {plan}")
        if billing_cycle not in VALID_CYCLES:
            raise ValueError(f"Ciclo inválido: {billing_cycle}")

        plan_id    = self._paypal.get_plan_id(plan, billing_cycle)
        return_url = f"{settings.FRONTEND_URL}/billing/success?provider=paypal"
        cancel_url = f"{settings.FRONTEND_URL}/planes"

        subscription_id = await self._paypal.create_subscription(
            plan_id=plan_id,
            user_id=user_id,
            return_url=return_url,
            cancel_url=cancel_url,
        )

        existing = await self._repo.get_by_user_id(user_id)
        if existing:
            await self._repo.update(
                user_id=user_id,
                plan=plan,
                billing_cycle=billing_cycle,
                paypal_subscription_id=subscription_id,
                payment_provider="paypal",
                status="incomplete",
            )
        else:
            await self._repo.create_paypal(
                user_id=user_id,
                paypal_subscription_id=subscription_id,
                plan=plan,
                billing_cycle=billing_cycle,
            )

        logger.info(f"[PayPal] Suscripción iniciada para usuario {user_id}: {subscription_id}")
        return subscription_id
