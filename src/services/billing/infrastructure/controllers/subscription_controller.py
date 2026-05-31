from src.core.database import AsyncSessionLocal
from src.services.billing.application.usecase.cancel_subscription_use_case import (
    CancelSubscriptionUseCase,
)
from src.services.billing.application.usecase.get_subscription_use_case import (
    GetSubscriptionUseCase,
)
from src.services.billing.infrastructure.adapters.MySQL import BillingRepository
from src.services.billing.infrastructure.adapters.stripe_adapter import StripeAdapter


async def get_subscription(current_user: dict) -> dict | None:
    repo         = BillingRepository(AsyncSessionLocal)
    subscription = await GetSubscriptionUseCase(repo).execute(current_user["user_id"])
    if not subscription:
        return None
    return {
        "plan":                subscription.plan,
        "billing_cycle":       subscription.billing_cycle,
        "status":              subscription.status,
        "current_period_end":  subscription.current_period_end,
        "cancel_at_period_end": subscription.cancel_at_period_end,
    }


async def cancel_subscription(current_user: dict) -> dict:
    repo   = BillingRepository(AsyncSessionLocal)
    stripe = StripeAdapter()
    await CancelSubscriptionUseCase(repo, stripe).execute(current_user["user_id"])
    return {"message": "Suscripción cancelada al final del período actual"}
