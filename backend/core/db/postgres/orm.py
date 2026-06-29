import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from uuid6 import uuid7

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
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    pwdhash: Mapped[str] = mapped_column(String, nullable=False)
    
    role = relationship("Role", lazy="joined")

# Таблица метаданных файлов и результатов парсинга
class Document(Base):
    __tablename__ = "documents"
    
    id: Mapped[uuid7] = mapped_column(primary_key=True, default=uuid7)
    owner_id: Mapped[uuid7] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    # Метаданные файла
    original_name: Mapped[str] = mapped_column(String(255))
    s3_bucket: Mapped[str] = mapped_column(String(100))
    s3_key: Mapped[str] = mapped_column(String(500))                   # Путь к файлу внутри MinIO (обычно UUID)
    content_type: Mapped[str] = mapped_column(String(100))
    
    # Результаты парсинга (структурированные данные, пока не уверен как это будет реализовано на самом деле)
    # status: Mapped[str] = mapped_column(String(50), default="pending") # pending, processing, completed, failed
    # parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)