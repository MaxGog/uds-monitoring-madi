from typing import Generic, List, TypeVar
import uuid

from pydantic import BaseModel, EmailStr

class UserCreateDTO(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponseDTO(BaseModel):
    id: str #uuid.UUID конвертация происходит на уровне БД пока что
    username: str
    email: EmailStr
    role: str
    company: str = 'Some company'
    position: str = 'Some position'
    status: str = 'Some status'

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