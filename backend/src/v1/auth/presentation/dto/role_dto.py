from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, Field

from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType

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

class RoleUpdateRequest(BaseModel):
    """Схема для частичного обновления роли (PATCH)"""
    name: str = Field(default=None, min_length=2, max_length=50)
    scope: ScopeType = Field(default=None)
    # Если поле передано как [], мы очистим права. Если не передано вообще — не трогаем.
    permissions: Optional[List[PermissionCreate]] = Field(default=None)

class RoleResponse(BaseModel):
    id: int
    name: str
    scope: ScopeType
    permissions: List[PermissionCreate] # Или ваша flat-схема ответа

    class Config:
        from_attributes = True