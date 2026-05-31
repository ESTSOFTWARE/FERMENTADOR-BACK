from datetime import datetime

from pydantic import BaseModel


class CreateCheckoutRequest(BaseModel):
    plan:          str   # starter | academic | enterprise
    billing_cycle: str   # monthly | annual


class CreatePayPalSubscriptionRequest(BaseModel):
    plan:          str   # starter | academic | enterprise
    billing_cycle: str   # monthly | annual


class CreatePayPalOrderRequest(BaseModel):
    amount:      str
    currency:    str = "MXN"
    description: str


class PayPalCaptureRequest(BaseModel):
    order_id: str


class SubscriptionResponse(BaseModel):
    plan:                   str
    billing_cycle:          str
    status:                 str
    current_period_end:     datetime | None = None
    cancel_at_period_end:   bool = False
    payment_provider:       str = "stripe"
    paypal_subscription_id: str | None = None


class SupportSubscriptionResponse(BaseModel):
    id:                     int
    user_id:                int
    stripe_customer_id:     str | None
    stripe_subscription_id: str | None
    paypal_subscription_id: str | None
    payment_provider:       str
    plan:                   str
    billing_cycle:          str
    status:                 str
    current_period_end:     datetime | None
    cancel_at_period_end:   bool
    created_at:             datetime
