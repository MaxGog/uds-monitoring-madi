from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, String, Table, Text, func

from backend.core.db.postgres.base_orm import Base
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

class TaskStatus(str, enum.Enum):
    PENDING = 'pending'
    STARTED = 'started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    PAUSED = 'paused'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'
    FAILED = 'failed'
    
class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

task_performers = Table(
    "task_performers",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Основная информация
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Статус и приоритет с использованием Enum
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status_enum", native_enum=True),
        default=TaskStatus.PENDING,
        nullable=False
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, name="task_priority_enum", native_enum=True),
        default=TaskPriority.MEDIUM,
        nullable=False
    )
    
    # Внешний ключ на создателя задачи (User)
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Внешний ключ на исполнителей задачи (может быть пустым)
    performers: Mapped[list["User"]] = relationship(
        "User", 
        secondary=task_performers, 
        back_populates="assigned_tasks"
    )
    
    # Временные метки (Таймстампы)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    author: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[author_id], 
        back_populates="created_tasks"
    )


# class TaskComment(Base):
#     __tablename__ = "task_comments"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
#     user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     comment_text: Mapped[str] = mapped_column(Text, nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     task: Mapped[Task] = relationship(back_populates="comments")
#     user: Mapped[Optional[User]] = relationship()