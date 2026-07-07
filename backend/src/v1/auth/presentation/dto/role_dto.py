from typing import List

from pydantic import BaseModel


class RoleResponse(BaseModel):
    id: int
    name: str

class RolesResponse(BaseModel):
    roles: List[RoleResponse]

class RoleCreateResponse(BaseModel):
    id: int
    name: str

class RoleUpdateResponse(BaseModel):
    id: int
    name: str

class RoleDeleteResponse(BaseModel):
    id: int
    name: str