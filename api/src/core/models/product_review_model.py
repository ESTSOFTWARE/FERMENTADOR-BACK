from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ProductReviewModel(Base):
    __tablename__ = "product_reviews"

    id:         Mapped[int]        = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int]        = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    user_id:    Mapped[int]        = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating:     Mapped[int]        = mapped_column(Integer, nullable=False)
    comment:    Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime]   = mapped_column(TIMESTAMP, nullable=False)