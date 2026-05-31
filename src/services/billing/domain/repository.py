from abc import ABC, abstractmethod

from src.services.billing.domain.entities.subscription import Subscription


class IBillingRepository(ABC):

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Subscription | None: ...

    @abstractmethod
    async def get_by_stripe_customer_id(self, customer_id: str) -> Subscription | None: ...

    @abstractmethod
    async def get_by_stripe_subscription_id(self, subscription_id: str) -> Subscription | None: ...

    @abstractmethod
    async def get_by_paypal_subscription_id(self, subscription_id: str) -> Subscription | None: ...

    @abstractmethod
    async def create(
        self,
        user_id:            int,
        stripe_customer_id: str,
        plan:               str,
        billing_cycle:      str,
    ) -> Subscription: ...

    @abstractmethod
    async def create_paypal(
        self,
        user_id:               int,
        paypal_subscription_id: str,
        plan:                  str,
        billing_cycle:         str,
    ) -> Subscription: ...

    @abstractmethod
    async def update(
        self,
        user_id:                int,
        stripe_subscription_id: str | None = None,
        plan:                   str | None = None,
        billing_cycle:          str | None = None,
        status:                 str | None = None,
        current_period_end:     object     = None,
        cancel_at_period_end:   bool | None = None,
        paypal_subscription_id: str | None = None,
        payment_provider:       str | None = None,
    ) -> Subscription: ...

    @abstractmethod
    async def list_all(
        self,
        status: str | None = None,
        plan:   str | None = None,
        limit:  int = 50,
        offset: int = 0,
    ) -> list[Subscription]: ...
