from sqlalchemy import Column, DateTime, Integer, String, Text, Double, text
from src.core.database import Base

class ProductModel(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    price       = Column(Double, nullable=False)
    sku         = Column(String(50), nullable=False, unique=True)
    stock       = Column(Integer, nullable=False, server_default=text("0"), default=0)
    rating      = Column(Integer, nullable=False, server_default=text("1"), default=1)
    created_at  = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
