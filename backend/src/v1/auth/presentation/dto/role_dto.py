from enum import StrEnum
from typing import List

from pydantic import BaseModel, Field

from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType

class Permission(BaseModel):
    entity: EntityType
    action: ActionType

class PermissionCreate(BaseModel):
    """Схема для передачи конкретного права"""
    entity: EntityType = Field(
        ..., 
        description="Сущность, на которую дается право (например, 'user', 'report')"
    )
    action: ActionType = Field(
        ..., 
        description="Действие, которое разрешено (например, 'read', 'create')"
    )

class RoleResponse(BaseModel):
    id: int
    name: str

class RolesResponse(BaseModel):
    roles: List[RoleResponse]

class RoleCreateResponse(BaseModel):
    id: int
    name: str
    scope: ScopeType = Field(
        default=ScopeType.LOCAL, 
        description="Область действия роли. GLOBAL — для глобальных, LOCAL — для кастомных"
    )

    permissions: List[PermissionCreate] = Field(
        default_factory=list, 
        description="Список прав, привязанных к роли. Может быть пустым."
    )

class RoleUpdateResponse(BaseModel):
    id: int
    name: str

class RoleDeleteResponse(BaseModel):
    id: int
    name: str

class RoleCreateRequest(BaseModel):
    """Схема создания новой роли"""
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=50, 
        description="Уникальное название роли (например, 'manager', 'global_auditor')"
    )
    scope: ScopeType = Field(
        default=ScopeType.LOCAL, 
        description="Область действия роли. GLOBAL — для глобальных, LOCAL — для кастомных"
    )

    permissions: List[PermissionCreate] = Field(
        default_factory=list, 
        description="Список прав, привязанных к роли. Может быть пустым."
    )