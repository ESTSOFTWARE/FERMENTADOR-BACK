from datetime import datetime

from sqlalchemy import DECIMAL, TIMESTAMP, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ProductModel(Base):
    __tablename__ = "products"

    id:          Mapped[int]        = mapped_column(Integer, primary_key=True)
    name:        Mapped[str]        = mapped_column(String(150), nullable=False)
    description: Mapped[str]        = mapped_column(Text, nullable=False)
    price:       Mapped[float]      = mapped_column(DECIMAL(10, 2), nullable=False)
    sku:         Mapped[str]        = mapped_column(String(50), nullable=False, unique=True)
    stock:       Mapped[int]        = mapped_column(Integer, nullable=False, default=0)
    rating:      Mapped[float]      = mapped_column(DECIMAL(3, 2), nullable=False, default=0)
    image:       Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("product_categories.id", ondelete="SET NULL"), default=None)
    created_at:  Mapped[datetime]   = mapped_column(TIMESTAMP, nullable=False)
    updated_at:  Mapped[datetime]   = mapped_column(TIMESTAMP, nullable=False)