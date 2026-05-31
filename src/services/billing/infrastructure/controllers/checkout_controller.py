from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.core.models.user_models import UserModel
from src.services.billing.application.usecase.create_checkout_session_use_case import (
    CreateCheckoutSessionUseCase,
)
from src.services.billing.domain.dto.billing_schema import CreateCheckoutRequest
from src.services.billing.infrastructure.adapters.MySQL import BillingRepository
from src.services.billing.infrastructure.adapters.stripe_adapter import StripeAdapter


async def create_checkout(body: CreateCheckoutRequest, current_user: dict) -> dict:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(UserModel.email, UserModel.name).where(
                UserModel.id == current_user["user_id"]
            )
        )
        row = result.one()

    repo   = BillingRepository(AsyncSessionLocal)
    stripe = StripeAdapter()
    url    = await CreateCheckoutSessionUseCase(repo, stripe).execute(
        user_id=current_user["user_id"],
        user_email=row.email,
        user_name=row.name,
        plan=body.plan,
        billing_cycle=body.billing_cycle,
    )
    return {"client_secret": url}
