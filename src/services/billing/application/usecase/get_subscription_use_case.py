from src.services.billing.domain.entities.subscription import Subscription
from src.services.billing.domain.repository import IBillingRepository


class GetSubscriptionUseCase:

    def __init__(self, repository: IBillingRepository):
        self._repo = repository

    async def execute(self, user_id: int) -> Subscription | None:
        return await self._repo.get_by_user_id(user_id)
