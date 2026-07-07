from datetime import datetime
import enum
from typing import Optional
from sqlalchemy import Column, DateTime, Enum, Integer, String, ForeignKey, Table, Text, func
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid6

from backend.core.db.postgres.base_orm import Base
from backend.core.db.postgres.data_orms.task_orm import Task, task_performers
from backend.src.v1.auth.domain.models import UserStatus


class RoleName(str, enum.Enum):
    ADMIN = "admin"
    VIEWER = "viewer"
    USER = "user" # Custom, global meaning

class FileAccessType(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    UPDATE = 'update'

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid6.uuid7
    )
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    position_name: Mapped[Optional[str]] = mapped_column(Text)
    department: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, name="user_status", native_enum=True), nullable=False, server_default="active")
    role_id = Column(Integer, ForeignKey("roles.id"))
    pwdhash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Tasks
    created_tasks: Mapped[list["Task"]] = relationship("Task", foreign_keys=[Task.author_id], back_populates="author")
    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task", 
        secondary=task_performers, 
        back_populates="performers"
    )

    # Roles
    role = relationship("Role", lazy="joined")
    
# Промежуточная таблица для связи Ролей и Прав (Many-to-Many)
# Используется модель RBAC и для гибкости через промежуточную таблицу, чтобы можно было всегда добавить/удалить права или роль
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE")),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE")),
)

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # Например: "user:create", "user:view"

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # Например: "admin", "viewer"
    
    # Связь с правами
    permissions = relationship("Permission", secondary=role_permissions, lazy="joined")

# Таблица метаданных файлов и результатов парсинга
class Document(Base):
    __tablename__ = "documents"
    
    # Использование uuid позволит в случае чего разделить на несколько серверов данные.
    # 7 версия имеет полезный функционал в виде генерации временной метки в начале идентификатора
    # и в дальнейшем делить эффективнее данные через индекс
    id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid6.uuid7
    )
    owner_id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    
    # Метаданные файла
    name: Mapped[str] = mapped_column(String(255))
    s3_bucket: Mapped[str] = mapped_column(String(100))
    s3_key: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(100))
    
    # Результаты парсинга (структурированные данные, пока не уверен как это будет реализовано на самом деле)
    #status: Mapped[str] = mapped_column(String(50), default="pending")
    #parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)



# class User(Base):
#     __tablename__ = "users"

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
#     email: Mapped[str] = mapped_column(CITEXT(), unique=True, nullable=False)
#     password_hash: Mapped[str] = mapped_column(Text, nullable=False)
#     full_name: Mapped[str] = mapped_column(Text, nullable=False)
#     position_name: Mapped[Optional[str]] = mapped_column(Text)
#     department: Mapped[Optional[str]] = mapped_column(Text)
#     role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role", native_enum=True), nullable=False, server_default="viewer")
#     status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, name="user_status", native_enum=True), nullable=False, server_default="active")
#     last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
#     deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

#     sessions: Mapped[list[UserSession]] = relationship(back_populates="user", cascade="all, delete-orphan")
#     created_objects: Mapped[list[RoadObject]] = relationship(foreign_keys="RoadObject.created_by", back_populates="creator")
#     tasks_created: Mapped[list[Task]] = relationship(foreign_keys="Task.created_by", back_populates="creator")
# #     assigned_tasks: Mapped[list[TaskAssignee]] = relationship(back_populates="user", cascade="all, delete-orphan")

# class UserSession(Base):
#     __tablename__ = "user_sessions"

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
#     user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     refresh_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
#     user_agent: Mapped[Optional[str]] = mapped_column(Text)
#     ip_address: Mapped[Optional[str]] = mapped_column(INET())
#     expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
#     revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     user: Mapped[User] = relationship(back_populates="sessions")

# class LoginAudit(Base):
#     __tablename__ = "login_audit"

#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     email: Mapped[str] = mapped_column(CITEXT(), nullable=False)
#     success: Mapped[bool] = mapped_column(Boolean, nullable=False)
#     failure_reason: Mapped[Optional[str]] = mapped_column(Text)
#     ip_address: Mapped[Optional[str]] = mapped_column(INET())
#     user_agent: Mapped[Optional[str]] = mapped_column(Text)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

#     user: Mapped[Optional[User]] = relationship()

