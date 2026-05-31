import logging

from src.core.config import settings
from src.services.billing.domain.repository import IBillingRepository
from src.services.billing.infrastructure.adapters.stripe_adapter import StripeAdapter

logger = logging.getLogger(__name__)

VALID_PLANS  = {"starter", "academic", "enterprise"}
VALID_CYCLES = {"monthly", "annual"}


class CreateCheckoutSessionUseCase:

    def __init__(self, repository: IBillingRepository, stripe: StripeAdapter):
        self._repo   = repository
        self._stripe = stripe

    async def execute(
        self,
        user_id:       int,
        user_email:    str,
        user_name:     str,
        plan:          str,
        billing_cycle: str,
    ) -> str:
        if plan not in VALID_PLANS:
            raise ValueError(f"Plan inválido: {plan}")
        if billing_cycle not in VALID_CYCLES:
            raise ValueError(f"Ciclo de facturación inválido: {billing_cycle}")

        subscription = await self._repo.get_by_user_id(user_id)

        if subscription:
            customer_id = subscription.stripe_customer_id
        else:
            customer_id = self._stripe.create_customer(user_email, user_name)
            await self._repo.create(
                user_id=user_id,
                stripe_customer_id=customer_id,
                plan=plan,
                billing_cycle=billing_cycle,
            )

        price_id   = self._stripe.get_price_id(plan, billing_cycle)
        return_url = f"{settings.FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"

        client_secret = self._stripe.create_checkout_session(
            customer_id=customer_id,
            price_id=price_id,
            user_id=user_id,
            return_url=return_url,
        )
        logger.info(f"[Billing] Checkout creado para usuario {user_id} — plan {plan}/{billing_cycle}")
        return client_secret
