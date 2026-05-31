from sqlalchemy import select, update

from src.core.models.billing_models import SubscriptionModel
from src.services.billing.domain.entities.subscription import Subscription
from src.services.billing.domain.repository import IBillingRepository


class BillingRepository(IBillingRepository):

    def __init__(self, session_factory):
        self._session_factory = session_factory

    def _to_entity(self, m: SubscriptionModel) -> Subscription:
        return Subscription(
            id=m.id,
            user_id=m.user_id,
            stripe_customer_id=m.stripe_customer_id,
            stripe_subscription_id=m.stripe_subscription_id,
            plan=m.plan,
            billing_cycle=m.billing_cycle,
            status=m.status,
            current_period_end=m.current_period_end,
            cancel_at_period_end=bool(m.cancel_at_period_end),
            created_at=m.created_at,
        )

    async def get_by_user_id(self, user_id: int) -> Subscription | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(SubscriptionModel).where(SubscriptionModel.user_id == user_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_by_stripe_customer_id(self, customer_id: str) -> Subscription | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(SubscriptionModel).where(
                    SubscriptionModel.stripe_customer_id == customer_id
                )
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_by_stripe_subscription_id(self, subscription_id: str) -> Subscription | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(SubscriptionModel).where(
                    SubscriptionModel.stripe_subscription_id == subscription_id
                )
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def create(
        self,
        user_id:            int,
        stripe_customer_id: str,
        plan:               str,
        billing_cycle:      str,
    ) -> Subscription:
        async with self._session_factory() as session:
            model = SubscriptionModel(
                user_id=user_id,
                stripe_customer_id=stripe_customer_id,
                plan=plan,
                billing_cycle=billing_cycle,
                status="incomplete",
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def update(
        self,
        user_id:                int,
        stripe_subscription_id: str | None = None,
        plan:                   str | None = None,
        billing_cycle:          str | None = None,
        status:                 str | None = None,
        current_period_end:     object     = None,
        cancel_at_period_end:   bool | None = None,
    ) -> Subscription:
        values: dict = {}
        if stripe_subscription_id is not None:
            values["stripe_subscription_id"] = stripe_subscription_id
        if plan is not None:
            values["plan"] = plan
        if billing_cycle is not None:
            values["billing_cycle"] = billing_cycle
        if status is not None:
            values["status"] = status
        if current_period_end is not None:
            values["current_period_end"] = current_period_end
        if cancel_at_period_end is not None:
            values["cancel_at_period_end"] = cancel_at_period_end

        async with self._session_factory() as session:
            await session.execute(
                update(SubscriptionModel)
                .where(SubscriptionModel.user_id == user_id)
                .values(**values)
            )
            await session.commit()

        return await self.get_by_user_id(user_id)

    async def list_all(
        self,
        status: str | None = None,
        plan:   str | None = None,
        limit:  int = 50,
        offset: int = 0,
    ) -> list[Subscription]:
        async with self._session_factory() as session:
            query = select(SubscriptionModel)
            if status:
                query = query.where(SubscriptionModel.status == status)
            if plan:
                query = query.where(SubscriptionModel.plan == plan)
            query = query.order_by(SubscriptionModel.created_at.desc()).limit(limit).offset(offset)
            result = await session.execute(query)
            return [self._to_entity(m) for m in result.scalars().all()]
