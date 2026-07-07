from typing import Generic, TypeVar
import uuid

from pydantic import BaseModel, EmailStr

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    data: T

class BaseRequest(BaseModel, Generic[T]):
   data: T

class UserResponse(BaseModel):
    id: str #uuid.UUID конвертация происходит на уровне БД пока что
    username: str
    email: EmailStr
    role: str | None
    full_name: str | None
    company: str | None
    position: str | None
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

class UserCreateRequest(BaseModel):
    username: str = 'Pavel'
    email: EmailStr ='admin@madi.ru'
    password: str = 'secret'
    full_name: str | None = 'Pavel Pavlov Pavlovich'
    role: str | None = 'admin'
    position: str | None = 'Developer'
    company_id: int | None = None

class UserUpdateRequest(BaseModel):
    id: str
    username: str | None
    email: EmailStr | None
    role: str | None
    full_name: str | None
    company: str | None
    position: str | None
    status: str | None

class UserDeleteRequest(BaseModel):
    user_id: str

class UserRestoreRequest(BaseModel):
    user_id: str