import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

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

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    
    role = relationship("Role", lazy="joined")