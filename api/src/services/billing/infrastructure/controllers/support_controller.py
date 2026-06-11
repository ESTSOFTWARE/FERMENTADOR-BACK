from src.core.database import AsyncSessionLocal
from src.services.billing.application.usecase.list_subscriptions_use_case import (
    ListSubscriptionsUseCase,
)
from src.services.billing.infrastructure.adapters.postgres import BillingRepository


async def list_subscriptions(
    status: str | None = None,
    plan:   str | None = None,
    limit:  int = 50,
    offset: int = 0,
) -> list[dict]:
    repo = BillingRepository(AsyncSessionLocal)
    subs = await ListSubscriptionsUseCase(repo).execute(
        status=status, plan=plan, limit=limit, offset=offset
    )
    return [
        {
            "id":                     s.id,
            "user_id":                s.user_id,
            "stripe_customer_id":     s.stripe_customer_id,
            "stripe_subscription_id": s.stripe_subscription_id,
            "plan":                   s.plan,
            "billing_cycle":          s.billing_cycle,
            "status":                 s.status,
            "current_period_end":     s.current_period_end,
            "cancel_at_period_end":   s.cancel_at_period_end,
            "created_at":             s.created_at,
        }
        for s in subs
    ]
