from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, text

from src.core.database import Base


class AnnouncementModel(Base):
    __tablename__ = "announcements"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    label        = Column(String(50),  nullable=False)
    version      = Column(String(20),  nullable=False)
    date         = Column(String(20),  nullable=False)
    title        = Column(String(150), nullable=False)
    description  = Column(Text,        nullable=False)
    created_at   = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    is_pinned    = Column(Boolean,  nullable=False, default=False, server_default=text("false"))
    pinned_until = Column(DateTime, nullable=True)
