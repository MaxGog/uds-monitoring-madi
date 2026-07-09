from datetime import datetime
from typing import Generic, Optional, TypeVar
import uuid

from pydantic import BaseModel, EmailStr, Field

from backend.src.v1.auth.domain.models import UserStatus

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    data: T

class BaseRequest(BaseModel, Generic[T]):
   data: T

# --- CREATE ---
class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_\-]+$")
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    password: str = Field(..., min_length=8, max_length=128, description="Пароль в открытом виде")
    role_id: Optional[int] = Field(None)
    full_name: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=100)
    company_id: Optional[int] = Field(None)
    status: UserStatus = Field(default=UserStatus.ACTIVE)

# --- UPDATE (PATCH) ---
class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_\-]+$")
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    role_id: Optional[int] = Field(default=None)
    full_name: Optional[str] = Field(default=None, max_length=255)
    position: Optional[str] = Field(default=None, max_length=100)
    company_id: Optional[int] = Field(default=None)
    status: Optional[UserStatus] = Field(default=None)

# --- RESPONSE ---
class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    position: Optional[str] = None
    status: UserStatus
    company_id: Optional[int] = None
    role_id: Optional[int] = None
    
    # Автоматически заполняются из @property модели User
    role_name: Optional[str] = None
    company_name: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True