from dataclasses import dataclass
from typing import List

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.role_orm import RoleName
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IPasswordHasher, IUserRepo, IUserUsecases
from backend.src.v1.auth.presentation.dto.user_dto import UserCreateDTO, UserResponseDTO


@dataclass
class UserUsecases(IUserUsecases):
    uow: IUnitOfWork
    hasher: IPasswordHasher
    user_repo: IUserRepo

    async def get_me(self, user_id) -> UserResponseDTO:
        result = await self.user_repo.get_by_id(user_id)
        return result

    async def get_users(self, user_id: str, limit: int = 20, offset: int = 0) -> List[UserResponseDTO]:
        role = await self.user_repo.get_role(user_id)

        if role not in (RoleName.VIEWER, RoleName.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        # Выполнить проверку прав доступа для кастомной роли
        
        return await self.user_repo.get_all(limit = limit, offset = offset)
    
    async def create_user(self, creator_id: str, data: UserCreateDTO, ) -> UserResponseDTO:
        role = await self.user_repo.get_role(creator_id)

        if role == RoleName.VIEWER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        if role != RoleName.ADMIN:
            # Выполнить проверку прав доступа для кастомной роли по ACL
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        async with self.uow as uow:
            existing_user = await uow.users.get_by_email(data.email)
            if existing_user:
                raise HTTPException(status_code=409, detail='username or email already exists')
            password_hash_str = self.hasher.hash_password(data.password)
            data.password = password_hash_str
            user = await uow.users.create_user(data)
        return user

