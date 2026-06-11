from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, func, text
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
    payment_provider       = Column(Enum("stripe", "paypal", native_enum=False), nullable=False, default="stripe")
    plan                   = Column(Enum("starter", "academic", "enterprise", native_enum=False), nullable=False)
    billing_cycle          = Column(Enum("monthly", "annual", native_enum=False), nullable=False, default="monthly")
    status                 = Column(
        Enum("active", "past_due", "canceled", "incomplete", native_enum=False),
        nullable=False,
        default="incomplete",
    )
    current_period_end  = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=False,
                                   server_default=text("false"), default=False)
    created_at          = Column(DateTime, nullable=False,
                                  server_default=text("CURRENT_TIMESTAMP"))
    updated_at          = Column(DateTime, nullable=False,
                                  server_default=text("CURRENT_TIMESTAMP"), onupdate=func.now())

    user = relationship("UserModel", backref="subscription")
