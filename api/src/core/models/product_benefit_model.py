from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ProductBenefitModel(Base):
    __tablename__ = "product_benefits"

    id:          Mapped[int]        = mapped_column(Integer, primary_key=True)
    product_id:  Mapped[int]        = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    title:       Mapped[str]        = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    created_at:  Mapped[datetime]   = mapped_column(TIMESTAMP, nullable=False)