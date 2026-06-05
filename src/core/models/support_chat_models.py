from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import relationship

from src.core.database import Base


class SupportConversationModel(Base):
    __tablename__ = "support_conversations"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    admin_id             = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                                  nullable=False, unique=True)
    created_at           = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at           = Column(DateTime, nullable=False,
                                  server_default=text("CURRENT_TIMESTAMP"), onupdate=func.now())
    last_read_admin_at   = Column(DateTime, nullable=True)
    last_read_support_at = Column(DateTime, nullable=True)

    admin    = relationship("UserModel", foreign_keys=[admin_id])
    messages = relationship(
        "SupportMessageModel",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class SupportMessageModel(Base):
    __tablename__ = "support_messages"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("support_conversations.id", ondelete="CASCADE"),
                             nullable=False, index=True)
    sender_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_role     = Column(Enum("admin", "soporte", native_enum=False), nullable=False)
    content         = Column(Text, nullable=True)
    created_at      = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    conversation = relationship("SupportConversationModel", back_populates="messages")
    sender       = relationship("UserModel", foreign_keys=[sender_id])
    attachments  = relationship(
        "SupportMessageAttachmentModel",
        back_populates="message",
        cascade="all, delete-orphan",
    )


class SupportMessageAttachmentModel(Base):
    __tablename__ = "support_message_attachments"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("support_messages.id", ondelete="CASCADE"), nullable=False)
    type       = Column(Enum("image", "video", "document", "file", native_enum=False), nullable=False)
    name       = Column(String(255), nullable=False)
    url        = Column(String(2048), nullable=False)
    size       = Column(Integer, nullable=False, server_default=text("0"))

    message = relationship("SupportMessageModel", back_populates="attachments")
