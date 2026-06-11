import logging

from src.core.config import settings
from src.services.billing.infrastructure.adapters.paypal_adapter import PayPalAdapter

logger = logging.getLogger(__name__)


class CreatePayPalOrderUseCase:

    def __init__(self, paypal: PayPalAdapter):
        self._paypal = paypal

    async def execute(
        self,
        amount:      str,
        currency:    str,
        description: str,
    ) -> str:
        return_url = f"{settings.FRONTEND_URL}/billing/order-success"
        cancel_url = f"{settings.FRONTEND_URL}/products"

        order_id = await self._paypal.create_order(
            amount=amount,
            currency=currency,
            description=description,
            return_url=return_url,
            cancel_url=cancel_url,
        )
        logger.info(f"[PayPal] Orden creada: {order_id}")
        return order_id
