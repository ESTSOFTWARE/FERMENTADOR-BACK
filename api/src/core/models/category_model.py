from datetime import datetime

from sqlalchemy import TIMESTAMP, Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ProductCategoryModel(Base):
    __tablename__ = "product_categories"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    name:        Mapped[str]           = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None]    = mapped_column(Text, default=None)
    created_at:  Mapped[datetime]      = mapped_column(TIMESTAMP, nullable=False)
    updated_at:  Mapped[datetime]      = mapped_column(TIMESTAMP, nullable=False)