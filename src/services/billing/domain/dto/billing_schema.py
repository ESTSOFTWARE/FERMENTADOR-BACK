from datetime import datetime

from pydantic import BaseModel


class CreateCheckoutRequest(BaseModel):
    plan:          str   # starter | academic | enterprise
    billing_cycle: str   # monthly | annual


class SubscriptionResponse(BaseModel):
    plan:                str
    billing_cycle:       str
    status:              str
    current_period_end:  datetime | None = None
    cancel_at_period_end: bool = False


class SupportSubscriptionResponse(BaseModel):
    id:                     int
    user_id:                int
    stripe_customer_id:     str
    stripe_subscription_id: str | None
    plan:                   str
    billing_cycle:          str
    status:                 str
    current_period_end:     datetime | None
    cancel_at_period_end:   bool
    created_at:             datetime
