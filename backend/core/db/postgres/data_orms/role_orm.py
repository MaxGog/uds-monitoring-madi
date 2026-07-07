import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String, ForeignKey, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db.postgres.base_orm import Base


class RoleName(str, enum.Enum):
    ADMIN = "admin"
    VIEWER = "viewer"
    USER = "user" # Custom, global meaning

class FileAccessType(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    UPDATE = 'update'
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
