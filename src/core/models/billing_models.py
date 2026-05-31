from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from src.core.database import Base


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    id                     = Column(Integer, primary_key=True, autoincrement=True)
    user_id                = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                                    nullable=False, unique=True)
    stripe_customer_id     = Column(String(100), nullable=True, unique=True)
    stripe_subscription_id = Column(String(100), nullable=True, unique=True)
    paypal_subscription_id = Column(String(100), nullable=True, unique=True)
    payment_provider       = Column(Enum("stripe", "paypal"), nullable=False, default="stripe")
    plan                   = Column(Enum("starter", "academic", "enterprise"), nullable=False)
    billing_cycle          = Column(Enum("monthly", "annual"), nullable=False, default="monthly")
    status                 = Column(
        Enum("active", "past_due", "canceled", "incomplete"),
        nullable=False,
        default="incomplete",
    )
    current_period_end  = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=False,
                                   server_default=text("0"), default=False)
    created_at          = Column(DateTime, nullable=False,
                                  server_default=text("CURRENT_TIMESTAMP"))
    updated_at          = Column(DateTime, nullable=False,
                                  server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    user = relationship("UserModel", backref="subscription")
