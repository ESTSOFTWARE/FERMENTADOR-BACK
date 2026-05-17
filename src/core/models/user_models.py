from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship

from src.core.database import Base


class RoleModel(Base):
    __tablename__ = "roles"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(50), nullable=False, unique=True)
    description = Column(String(150), nullable=True)

    users = relationship("UserModel", back_populates="role")


class UserModel(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String(100), nullable=False)
    last_name     = Column(String(100), nullable=False)
    password      = Column(String(255), nullable=True)
    email         = Column(String(150), nullable=False, unique=True)
    role_id       = Column(Integer, ForeignKey("roles.id"), nullable=False, default=3)
    circuit_id    = Column(Integer, ForeignKey("circuits.id"), nullable=True)
    created_by    = Column(Integer, ForeignKey("users.id"), nullable=True)
    profile_image = Column(Text, nullable=True)
    created_at    = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    oauth_google_id = Column(String(100), nullable=True)
    oauth_github_id = Column(String(100), nullable=True)

    role    = relationship("RoleModel", back_populates="users")
    creator = relationship("UserModel", remote_side=[id])
