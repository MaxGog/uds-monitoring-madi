from enum import StrEnum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType

# --- СХЕМА ПРАВА (ДЛЯ ОТВЕТА) ---
class PermissionResponse(BaseModel):
    id: int
    entity: EntityType
    action: ActionType

    model_config = ConfigDict(from_attributes=True)

class PermissionCreateRequest(BaseModel):
    entity: EntityType
    action: ActionType

# --- CREATE ---
class RoleCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Уникальное имя роли (например, 'manager')")
    scope: ScopeType = Field(default=ScopeType.LOCAL, description="Область видимости данных")
    permissions: Optional[List[Union[int, PermissionCreateRequest]]] = Field(
        None,
        description="Список ID прав или объектов {entity, action} для автосоздания и привязки"
    )

# --- UPDATE (PATCH) ---
class RoleUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    scope: Optional[ScopeType] = Field(default=None)
    permissions: Optional[List[Union[int, PermissionCreateRequest]]] = Field(None    )

# --- RESPONSE ---
class RoleResponse(BaseModel):
    id: int
    name: str
    scope: ScopeType
    permissions: List[PermissionResponse]

    model_config = ConfigDict(from_attributes=True)