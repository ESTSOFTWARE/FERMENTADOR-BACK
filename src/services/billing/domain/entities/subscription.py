from dataclasses import dataclass
from datetime import datetime


@dataclass
class Subscription:
    id:                     int
    user_id:                int
    stripe_customer_id:     str
    stripe_subscription_id: str | None
    plan:                   str   # starter | academic | enterprise
    billing_cycle:          str   # monthly | annual
    status:                 str   # active | past_due | canceled | incomplete
    current_period_end:     datetime | None
    cancel_at_period_end:   bool
    created_at:             datetime
