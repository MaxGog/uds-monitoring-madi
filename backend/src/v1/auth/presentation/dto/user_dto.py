from typing import Generic, Optional, TypeVar
import uuid

from pydantic import BaseModel, EmailStr, Field

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    data: T

class BaseRequest(BaseModel, Generic[T]):
   data: T

class UserResponse(BaseModel):
    id: str #uuid.UUID конвертация происходит на уровне БД пока что
    username: str
    email: EmailStr
    role: Optional[str]
    full_name: Optional[str]
    company: Optional[str]
    position: Optional[str]
    status: str = 'active'

    class Config:
        from_attributes = True

class UsersResponse(BaseModel):
    data: list[UserResponse]

class UserUpdateResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str | None
    full_name: str | None
    company: str | None
    position: str | None
    status: str

class UserRequest(BaseModel):
    id: str

class UserCreateRequest(BaseModel):
    username: str = 'Pavel'
    email: EmailStr ='admin@madi.ru'
    password: str = 'secret'
    full_name: str | None = 'Pavel Pavlov Pavlovich'
    role: str | None = 'admin'
    position: str | None = 'Developer'
    company_id: int | None = None

class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None

    full_name: Optional[str] = Field(default=None)
    position: Optional[str] = Field(default=None)
    company_id: Optional[int] = Field(default=None)
    role_id: Optional[int] = Field(default=None)
    status: Optional[str] = Field(default=None)

class UserDeleteRequest(BaseModel):
    user_id: str

class UserRestoreRequest(BaseModel):
    user_id: str