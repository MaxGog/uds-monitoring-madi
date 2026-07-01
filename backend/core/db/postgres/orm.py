import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid6

Base = declarative_base()

class RoleName(str, enum.Enum):
    ADMIN = "admin"
    VIEWER = "viewer"
    USER = "user"

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
    role_id = Column(Integer, ForeignKey("roles.id"))
    pwdhash: Mapped[str] = mapped_column(String, nullable=False)
    
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