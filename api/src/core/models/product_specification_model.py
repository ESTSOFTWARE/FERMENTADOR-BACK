from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ProductSpecificationModel(Base):
    __tablename__ = "product_specifications"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int]      = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    name:       Mapped[str]      = mapped_column(String(150), nullable=False)
    value:      Mapped[str]      = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)