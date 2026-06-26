from pydantic import BaseModel, EmailStr

class UserCreateDTO(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponseDTO(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True