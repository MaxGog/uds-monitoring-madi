from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, Field

from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType

# --- СХЕМА ПРАВА (ДЛЯ ОТВЕТА) ---
class PermissionResponse(BaseModel):
    id: int
    entity: EntityType
    action: ActionType

    class Config:
        from_attributes = True

# --- CREATE ---
class RoleCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Уникальное имя роли (например, 'manager')")
    scope: ScopeType = Field(default=ScopeType.LOCAL, description="Область видимости данных")
    permission_ids: List[int] = Field(default_factory=list, description="Список ID прав для привязки к роли")

# --- UPDATE (PATCH) ---
class RoleUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    scope: Optional[ScopeType] = Field(default=None)
    permission_ids: Optional[List[int]] = Field(
        default=None, 
        description="Полная перезапись прав роли. Если прислать [], все права будут сняты."
    )

# --- RESPONSE ---
class RoleResponse(BaseModel):
    id: int
    name: str
    scope: ScopeType
    permissions: List[PermissionResponse]

    class Config:
        from_attributes = True