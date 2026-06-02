from src.core.database import AsyncSessionLocal
from src.core.subscription_cache import subscription_cache
from src.services.billing.application.usecase.cancel_subscription_use_case import (
    CancelSubscriptionUseCase,
)
from src.services.billing.application.usecase.get_subscription_use_case import (
    GetSubscriptionUseCase,
)
from src.services.billing.infrastructure.adapters.MySQL import BillingRepository
from src.services.billing.infrastructure.adapters.stripe_adapter import StripeAdapter


async def get_subscription(current_user: dict) -> dict | None:
    user_id = current_user["user_id"]

    cached = subscription_cache.get(user_id)
    if cached is not None:
        return cached

    repo         = BillingRepository(AsyncSessionLocal)
    subscription = await GetSubscriptionUseCase(repo).execute(user_id)
    if not subscription:
        return None

    result = {
        "plan":                 subscription.plan,
        "billing_cycle":        subscription.billing_cycle,
        "status":               subscription.status,
        "current_period_end":   subscription.current_period_end,
        "cancel_at_period_end": subscription.cancel_at_period_end,
        "payment_provider":     subscription.payment_provider,
        "paypal_subscription_id": subscription.paypal_subscription_id,
    }
    subscription_cache.set(user_id, result)
    return result


async def cancel_subscription(current_user: dict) -> dict:
    user_id = current_user["user_id"]
    repo    = BillingRepository(AsyncSessionLocal)
    stripe  = StripeAdapter()
    await CancelSubscriptionUseCase(repo, stripe).execute(user_id)
    subscription_cache.invalidate(user_id)
    return {"message": "Suscripción cancelada al final del período actual"}
