import logging

from src.core.exceptions import BadRequestException, NotFoundException
from src.services.billing.domain.repository import IBillingRepository
from src.services.billing.infrastructure.adapters.stripe_adapter import StripeAdapter

logger = logging.getLogger(__name__)


class CancelSubscriptionUseCase:

    def __init__(self, repository: IBillingRepository, stripe: StripeAdapter):
        self._repo   = repository
        self._stripe = stripe

    async def execute(self, user_id: int) -> None:
        subscription = await self._repo.get_by_user_id(user_id)
        if not subscription:
            raise NotFoundException("No tienes una suscripción activa")

        if subscription.status == "canceled":
            raise BadRequestException("La suscripción ya está cancelada")

        if not subscription.stripe_subscription_id:
            raise BadRequestException("Suscripción sin ID de Stripe")

        self._stripe.cancel_subscription(subscription.stripe_subscription_id)
        await self._repo.update(user_id=user_id, cancel_at_period_end=True)
        logger.info(f"[Billing] Cancelación programada para usuario {user_id}")
