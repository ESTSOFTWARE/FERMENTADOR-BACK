from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ProductIncludeModel(Base):
    __tablename__ = "product_includes"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True)
    product_id:  Mapped[int]      = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str]      = mapped_column(Text, nullable=False)
    created_at:  Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)