from datetime import datetime
import enum
from typing import Optional
from sqlalchemy import Column, DateTime, Enum, Integer, String, ForeignKey, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid6

from backend.core.db.postgres.base_orm import Base
from backend.core.db.postgres.data_orms.copmany_orm import Company
from backend.core.db.postgres.data_orms.task_orm import Task, task_performers
from backend.src.v1.auth.domain.models import UserStatus


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid6.uuid7
    )
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    pwdhash: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("roles.id"), nullable=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=True)
    position: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, name="user_status", native_enum=True), nullable=False, server_default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Companies
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=True)
    company: Mapped["Company"] = relationship("Company", back_populates="users")

    # Tasks
    created_tasks: Mapped[list["Task"]] = relationship("Task", foreign_keys=[Task.author_id], back_populates="author")
    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task", 
        secondary=task_performers, 
        back_populates="performers"
    )
    # Roles
    role = relationship("Role", lazy="joined")

    @property
    def role_name(self) -> str | None:
        return self.role.name if self.role else None

    @property
    def company_name(self) -> str | None:
        return self.company.name if self.company else None
