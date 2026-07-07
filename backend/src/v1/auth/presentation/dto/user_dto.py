from typing import Generic, List, TypeVar
import uuid

from pydantic import BaseModel, EmailStr

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    data: T

class BaseRequest(BaseModel, Generic[T]):
   data: T

class UserCreateDTO(BaseModel):
    username: str = 'Pavel'
    email: EmailStr ='admin@madi.ru'
    password: str = 'secret'
    full_name: str | None = 'Pavel Pavlov Pavlovich'
    role: str | None = 'admin'
    position: str | None = 'Developer'
    company_id: int | None = None



class UserResponseDTO(BaseModel):
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

class UsersListResponse(BaseModel):
    data: list[UserResponseDTO]

class getUser(BaseModel):
  id: str
  email: str = "shitstorm@mail.com"
  username: str = "Faggot"
  role: str = "Abuser"
  company: str = "Shithole"
  position: str = "Retard"
  status: str = "Active"

class UserCreate(BaseModel):
  email: str
  username: str
  password: str | None
  role_id: int

class UserUpdate(BaseModel):
  email: str | None
  username: str | None
  role: str | None