from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import relationship

from src.core.database import Base


class GroupModel(Base):
    __tablename__ = "classrooms"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String(100), nullable=False)
    subject      = Column(String(100), nullable=False)
    cover_image  = Column(String(2048), nullable=True)
    professor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code         = Column(String(20), nullable=False, unique=True)
    created_at   = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    professor = relationship("UserModel", foreign_keys=[professor_id])
    members   = relationship("GroupMemberModel", back_populates="group", cascade="all, delete-orphan")


class GroupMemberModel(Base):
    __tablename__ = "group_members"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    group_id   = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at  = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint("student_id", name="uq_student_one_group"),
    )

    group   = relationship("GroupModel", back_populates="members")
    student = relationship("UserModel", foreign_keys=[student_id])
