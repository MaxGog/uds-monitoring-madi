from pydantic import BaseModel, EmailStr

class UserCreateDTO(BaseModel):
    email: EmailStr
    password: str

class UserResponseDTO(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True