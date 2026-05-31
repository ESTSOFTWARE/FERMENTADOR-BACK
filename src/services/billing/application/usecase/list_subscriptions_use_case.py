from src.services.billing.domain.entities.subscription import Subscription
from src.services.billing.domain.repository import IBillingRepository


class ListSubscriptionsUseCase:

    def __init__(self, repository: IBillingRepository):
        self._repo = repository

    async def execute(
        self,
        status: str | None = None,
        plan:   str | None = None,
        limit:  int = 50,
        offset: int = 0,
    ) -> list[Subscription]:
        return await self._repo.list_all(status=status, plan=plan, limit=limit, offset=offset)
