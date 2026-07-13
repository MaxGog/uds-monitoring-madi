from enum import StrEnum
from typing import List, Optional

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
    permissions: Optional[List[int]] = Field(default_factory=list, description="Список ID прав для привязки к роли")#Optional[List[PermissionCreateRequest]] = Field(default_factory=list, description="Список прав для создания")

# --- UPDATE (PATCH) ---
class RoleUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    scope: Optional[ScopeType] = Field(default=None)
    permissions: Optional[List[int]] = Field(default_factory=list, description="Список ID прав для привязки к роли") #Optional[List[PermissionCreateRequest]] = Field(default_factory=list, description="Список прав для создания")

# --- RESPONSE ---
class RoleResponse(BaseModel):
    id: int
    name: str
    scope: ScopeType
    permissions: List[PermissionResponse]

    model_config = ConfigDict(from_attributes=True)