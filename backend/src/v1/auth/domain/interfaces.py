from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Protocol
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db.postgres.data_orms.role_orm import Permission, Role
from backend.core.db.postgres.data_orms.user_orm import User
from backend.src.v1.auth.domain.models import CodeData
from backend.src.v1.auth.domain.role_models import ActionType, EntityType
from backend.src.v1.auth.presentation.dto.auth_dto import LoginResultDTO, RefreshSessionDTO
from backend.src.v1.auth.presentation.dto.role_dto import RoleCreateRequest, RoleResponse, RoleUpdateRequest
from backend.src.v1.auth.presentation.dto.user_dto import UserCreateRequest, UserResponse, UserUpdateRequest

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

@dataclass
class TokenData():
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
# Интерфейсы, можно легко подменять реализации и мокать

class IUserRepo(Protocol):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]: pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]: pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: pass
    
    @abstractmethod
    async def get_all(self) -> List[User]: pass
    
    @abstractmethod
    async def count_by_company(self, item_id: int) -> int: pass
    
    @abstractmethod
    async def count_by_role(self, item_id: int) -> int: pass

    @abstractmethod
    async def add(self, user: User) -> None: pass

    @abstractmethod
    async def hard_delete_by_email(self, email: str) -> None: pass

class IRoleRepo(Protocol):
    @abstractmethod
    async def get_by_id(self, role_id: int) -> Optional[Role]: pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Role]: pass

    @abstractmethod
    async def get_all(self) -> List[Role]: pass

    @abstractmethod
    async def add(self, role: Role) -> Role: pass

    @abstractmethod
    async def delete(self, role: Role) -> None: pass

class IUserUsecases(Protocol):
    @abstractmethod
    async def get_me(self, user_id: str) -> UserResponse:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        pass

    @abstractmethod
    async def get_all_users(self) -> List[UserResponse]:
        pass
    
    @abstractmethod
    async def create_user(self, data: UserCreateRequest) -> UserResponse:
        pass

    @abstractmethod
    async def update_user(self, user_id: UUID, data: UserUpdateRequest) -> UserResponse:
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def hard_delete_user_by_email(self, email: str) -> None: pass

class IPermissionRepo(Protocol):
    @abstractmethod
    async def get_by_ids(self, ids: List[int]) -> List[Permission]:
        """Получить список разрешений по их ID"""
        pass

    @abstractmethod
    async def get_by_entity_and_action(self, entity: EntityType, action: ActionType) -> Optional[Permission]:
        """Найти разрешение по уникальной паре (entity, action)"""
        pass

    @abstractmethod
    async def create(self, entity: EntityType, action: ActionType) -> Permission:
        """Создать новое разрешение в БД"""
        pass

    @abstractmethod
    async def add(self, permission: Permission) -> Permission:
        pass

    @abstractmethod
    async def delete_by_entity_and_action(self, entity: EntityType, action: ActionType) -> None:
        """Удалить разрешение по типу сущности и действию"""
        pass


class IRoleUsecases(Protocol):
    @abstractmethod
    async def create_role(self, data: RoleCreateRequest) -> RoleResponse:
        pass

    @abstractmethod
    async def get_role_by_id(self, item_id: int) -> RoleResponse:
        pass

    @abstractmethod
    async def get_all_roles(self) -> List[RoleResponse]:
        pass

    @abstractmethod
    async def update_role(self, item_id: int, data: RoleUpdateRequest) -> RoleResponse:
        pass

    @abstractmethod
    async def delete_role(self, item_id: int) -> None:
        pass

class ITokenProvider(Protocol):
    @abstractmethod
    def extract_payload(self, token: str, verify_exp: bool = True) -> dict | None:
        pass

    @abstractmethod
    def create_access_token(self, data) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self, data) -> str:
        pass

    ...

class ITokenStorage(Protocol):
    @abstractmethod
    async def get_and_delete_code(self, code: str) -> CodeData | None:
        pass

    @abstractmethod
    async def save_code(self, code: str, user_id: str, challenge: str, code_ttl: int = 600) -> str:
        pass

    @abstractmethod
    async def add_session(self, user_id: str, access_jti: str, refresh_jti: str, expire_seconds: int):
        pass

    @abstractmethod
    async def is_session_valid(self, user_id: str, r_jti: str, a_jti: str | None = None) -> bool:
        pass

    @abstractmethod
    async def rotate_session(self, user_id: str, old_value: str, new_value: str, expire_seconds: int):
        pass

    @abstractmethod
    async def remove_session(self, user_id: str, a_jti: str, r_jti: str):
        pass

    @abstractmethod
    async def remove_all_sessions(self, user_id: str):
        pass
    ...

class ITokenAuth(Protocol):
    @abstractmethod
    async def set_tokens(self, user_id: str | None = None) -> TokenData:
        pass

    @abstractmethod
    async def set_token(self, token: str, token_type: TokenType):
        pass

    @abstractmethod
    async def rotate_tokens(self, user_id: str, old_refresh_token: str, old_access_token: str | None = None) -> TokenData:
        pass

    @abstractmethod
    async def revoke_specific_session(self, access_token: str, refresh_token: str):
        pass

    @abstractmethod
    async def revoke_all_sessions(self, user_id: str) -> None:
        pass

    @abstractmethod
    async def is_token_valid(self, access_token: str) -> bool:
        pass

    @abstractmethod
    async def is_session_valid(self, refresh_token: str, access_token: str | None = None) -> bool:
        pass
    ...

class IAuthUsecases(Protocol):
    @abstractmethod
    async def register_new_user(self, data: UserCreateRequest) -> UserResponse:
        pass

    @abstractmethod
    async def login(self, email: str, password: str, code_challenge: str) -> str:
        pass

    @abstractmethod
    async def exchange_code_for_tokens(self, code: str, code_verifier: str) -> LoginResultDTO:
        pass

    @abstractmethod
    async def rotate_tokens(self, refresh_token: str, access_token: str | None = None) -> RefreshSessionDTO:
        pass
    ...

class IPasswordHasher(Protocol):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def validate_password(self, password: str, hashed_password: str) -> bool:
        pass
    ...

