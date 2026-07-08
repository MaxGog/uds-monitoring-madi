import enum
from typing import List

from sqlalchemy import Column, DateTime, Enum, Integer, String, ForeignKey, Table, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db.postgres.base_orm import Base
from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType

# Промежуточная таблица для связи Ролей и Прав (Many-to-Many)
# Используется модель RBAC и для гибкости через промежуточную таблицу, чтобы можно было всегда добавить/удалить права или роль
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

class Permission(Base):
    __tablename__ = "permissions"

    __table_args__ = (
        UniqueConstraint('entity', 'action', name='_entity_action_uc'),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    entity: Mapped[EntityType] = mapped_column(
        Enum(EntityType, name="entity_type_enum", native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    action: Mapped[ActionType] = mapped_column(
        Enum(ActionType, name="action_type_enum", native_enum=True, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )

class Role(Base):
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable = False)  # Например: "admin", "viewer"
    
    scope: Mapped[ScopeType] = mapped_column(
        Enum(ScopeType, name="scope_type_enum", native_enum=True),
        nullable=False,
        default=ScopeType.LOCAL
    )
    # Связь с правами
    permissions: Mapped[List[Permission]] = relationship(
        secondary=role_permissions, 
        lazy="selectin"
    )
