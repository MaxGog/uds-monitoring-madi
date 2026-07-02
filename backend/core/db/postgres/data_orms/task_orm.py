# from datetime import datetime
# from typing import Optional
# import uuid

# from sqlalchemy import UUID, DateTime, Enum, ForeignKey, String, Text, func

# from backend.core.db.postgres.orm import Base, User
# import enum
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# class TaskStatus(str, enum.Enum):
#     PENDING = 'pending'
#     STARTED = 'started'
#     IN_PROGRESS = 'in_progress'
#     COMPLETED = 'completed'
#     PAUSED = 'paused'
#     CANCELLED = 'cancelled'
#     EXPIRED = 'expired'
#     FAILED = 'failed'
    
# class TaskPriority(str, enum.Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"

# class Task(Base):
#     __tablename__ = "tasks"

#     id: Mapped[int] = mapped_column(primary_key=True)
    
#     # Основная информация
#     title: Mapped[str] = mapped_column(String(255), nullable=False)
#     description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
#     # Статус и приоритет с использованием Enum
#     status: Mapped[TaskStatus] = mapped_column(
#         Enum(TaskStatus, name="task_status_enum", native_enum=True),
#         default=TaskStatus.PENDING,
#         nullable=False
#     )
#     priority: Mapped[TaskPriority] = mapped_column(
#         Enum(TaskPriority, name="task_priority_enum", native_enum=True),
#         default=TaskPriority.MEDIUM,
#         nullable=False
#     )
    
#     # Внешний ключ на создателя задачи (User)
#     author_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), 
#         ForeignKey("users.id", ondelete="CASCADE"), 
#         nullable=False
#     )
    
#     # Внешний ключ на исполнителя задачи (может быть пустым)
#     performer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
#         UUID(as_uuid=True), 
#         ForeignKey("users.id", ondelete="SET NULL"), 
#         nullable=True
#     )
    
#     # Временные метки (Таймстампы)
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), 
#         server_default=func.now(), 
#         nullable=False
#     )
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), 
#         server_default=func.now(), 
#         onupdate=func.now(), 
#         nullable=False
#     )
#     completed_at: Mapped[Optional[datetime]] = mapped_column(
#         DateTime(timezone=True), 
#         nullable=True
#     )

#     author: Mapped[User] = relationship(
#         "User", 
#         foreign_keys=[author_id], 
#         back_populates="created_tasks"
#     )
#     performer: Mapped[Optional[User]] = relationship(
#         "User", 
#         foreign_keys=[performer_id], 
#         back_populates="assigned_tasks"
#     )

# # class Task(Base):
# #     __tablename__ = "tasks"

# #     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
# #     title: Mapped[str] = mapped_column(Text, nullable=False)
# #     description: Mapped[Optional[str]] = mapped_column(Text)
# #     status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, name="task_status", native_enum=True), nullable=False, server_default="active")
# #     priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority, name="task_priority", native_enum=True), nullable=False, server_default="normal")
# #     task_type: Mapped[Optional[str]] = mapped_column(Text)
# #     related_object_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("road_objects.id", ondelete="SET NULL"))
# #     deadline_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
# #     created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
# #     closed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
# #     closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
# #     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
# #     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
# #     deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

# #     related_object: Mapped[Optional[RoadObject]] = relationship(back_populates="tasks")
# #     creator: Mapped[Optional[User]] = relationship(foreign_keys=[created_by], back_populates="tasks_created")
# #     assignees: Mapped[list[TaskAssignee]] = relationship(back_populates="task", cascade="all, delete-orphan")
# #     comments: Mapped[list[TaskComment]] = relationship(back_populates="task", cascade="all, delete-orphan")


# # class TaskAssignee(Base):
# #     __tablename__ = "task_assignees"

# #     task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
# #     user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
# #     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# #     __table_args__ = (PrimaryKeyConstraint("task_id", "user_id"),)

# #     task: Mapped[Task] = relationship(back_populates="assignees")
# #     user: Mapped[User] = relationship(back_populates="assigned_tasks")


# # class TaskComment(Base):
# #     __tablename__ = "task_comments"

# #     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
# #     task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
# #     user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
# #     comment_text: Mapped[str] = mapped_column(Text, nullable=False)
# #     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# #     task: Mapped[Task] = relationship(back_populates="comments")
# #     user: Mapped[Optional[User]] = relationship()