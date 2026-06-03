from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship

from src.core.database import Base


class ChatConversationModel(Base):
    __tablename__ = "chat_conversations"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    type        = Column(Enum("personal", "group"), nullable=False)
    name        = Column(String(150), nullable=True)
    description = Column(String(500), nullable=True)
    avatar      = Column(String(2048), nullable=True)
    created_by  = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at  = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at  = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    members = relationship(
        "ChatConversationMemberModel",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class ChatConversationMemberModel(Base):
    __tablename__ = "chat_conversation_members"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at       = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    last_read_at    = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("conversation_id", "user_id", name="uq_conversation_member"),
    )

    conversation = relationship("ChatConversationModel", back_populates="members")
    user         = relationship("UserModel", foreign_keys=[user_id])


class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    content         = Column(Text, nullable=True)
    reply_to_id     = Column(Integer, ForeignKey("chat_messages.id"), nullable=True)
    priority        = Column(Enum("normal", "important", "urgent"), nullable=False, server_default="normal")
    pinned          = Column(Integer, nullable=False, server_default=text("0"))
    edited          = Column(Integer, nullable=False, server_default=text("0"))
    edited_at       = Column(DateTime, nullable=True)
    deleted         = Column(Integer, nullable=False, server_default=text("0"))
    created_at      = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    sender      = relationship("UserModel", foreign_keys=[sender_id])
    reply_to    = relationship("ChatMessageModel", remote_side=[id])
    attachments = relationship(
        "ChatMessageAttachmentModel",
        back_populates="message",
        cascade="all, delete-orphan",
    )
    reactions = relationship(
        "ChatMessageReactionModel",
        back_populates="message",
        cascade="all, delete-orphan",
    )


class ChatMessageAttachmentModel(Base):
    __tablename__ = "chat_message_attachments"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    type       = Column(Enum("image", "video", "document", "file"), nullable=False)
    name       = Column(String(255), nullable=False)
    url        = Column(String(2048), nullable=False)
    size       = Column(Integer, nullable=False, server_default=text("0"))

    message = relationship("ChatMessageModel", back_populates="attachments")


class ChatMessageReactionModel(Base):
    __tablename__ = "chat_message_reactions"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    emoji      = Column(String(16), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint("message_id", "user_id", "emoji", name="uq_message_user_emoji"),
    )

    message = relationship("ChatMessageModel", back_populates="reactions")
    user    = relationship("UserModel", foreign_keys=[user_id])
