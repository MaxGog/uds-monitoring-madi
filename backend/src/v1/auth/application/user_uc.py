from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from typing import List
from uuid import UUID

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.user_orm import User
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IPasswordHasher, IUserRepo, IUserUsecases
from backend.src.v1.auth.presentation.dto.user_dto import UserCreateRequest, UserResponse, UserUpdateRequest

logger = logging.getLogger(__file__)

@dataclass
class UserUsecases(IUserUsecases):
    uow: IUnitOfWork
    hasher: IPasswordHasher
    user_repo: IUserRepo

    async def get_me(self, user_id: UUID) -> UserResponse:
        result = await self.user_repo.get_by_id(user_id)
        return UserResponse.model_validate(result)

    # --- READ (SINGLE) ---
    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found or has been deleted")
        return UserResponse.model_validate(user)

    # --- READ (LIST) ---
    async def get_all_users(self) -> List[UserResponse]:
        users = await self.user_repo.get_all()
        return [UserResponse.model_validate(u) for u in users]
    
    # --- CREATE ---
    async def create_user(self, data: UserCreateRequest) -> UserResponse:
        logger.info(f"Registering user: {data.username}")
        
        async with self.uow as uow:
            # 1. Проверка уникальности логина и почты
            if await uow.user_repo.get_by_username(data.username):
                raise HTTPException(status_code=400, detail="Username already taken")
            if await uow.user_repo.get_by_email(data.email):
                raise HTTPException(status_code=400, detail="Email already registered")

            # 2. Валидация внешних ключей
            if data.company_id and not await uow.company_repo.get_by_id(data.company_id):
                raise HTTPException(status_code=400, detail=f"Company {data.company_id} not found")
            # Предполагаем наличие role_repo в вашем UOW
            if data.role_id and not await uow.role_repo.get_by_id(data.role_id):
                raise HTTPException(status_code=400, detail=f"Role {data.role_id} not found")

            # 3. Хэшируем пароль и создаем инстанс
            hashed_password = self.hasher.hash_password(data.password)
            
            new_user = User(
                username=data.username,
                email=data.email,
                pwdhash=hashed_password,
                role_id=data.role_id,
                full_name=data.full_name,
                position=data.position,
                company_id=data.company_id,
                status=data.status
            )
            
            await self.uow.user_repo.add(new_user)
            await self.uow.commit()
            
            # Перечитываем со связями для красивого ответа
            user = await self.uow.user_repo.get_by_id(new_user.id)
            return UserResponse.model_validate(user)
    
    # --- UPDATE (PATCH) ---
    async def update_user(self, user_id: UUID, data: UserUpdateRequest) -> UserResponse:
        logger.info(f"Patching user UUID: {user_id}")
        
        async with self.uow as uow:
            user = await uow.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                return UserResponse.model_validate(user)

            # Валидация измененного логина/почты на уникальность
            if "username" in update_data and update_data["username"] != user.username:
                if await uow.user_repo.get_by_username(update_data["username"]):
                    raise HTTPException(status_code=400, detail="Username already taken")
                    
            if "email" in update_data and update_data["email"] != user.email:
                if await uow.user_repo.get_by_email(update_data["email"]):
                    raise HTTPException(status_code=400, detail="Email already registered")

            # Валидация связей
            if "company_id" in update_data and update_data["company_id"]:
                if not await uow.company_repo.get_by_id(update_data["company_id"]):
                    raise HTTPException(status_code=400, detail="Company not found")
            if "role_id" in update_data and update_data["role_id"]:
                if not await uow.role_repo.get_by_id(update_data["role_id"]):
                    raise HTTPException(status_code=400, detail="Role not found")

            # Обработка смены пароля
            if "password" in update_data:
                raw_password = update_data.pop("password")
                user.pwdhash = self.hasher.hash_password(raw_password)

            # Применяем остальные поля
            for key, value in update_data.items():
                setattr(user, key, value)

            await self.uow.commit()
            
            # Перечитываем обновленное состояние
            user = await self.uow.user_repo.get_by_id(user_id)
            return UserResponse.model_validate(user)
        
    # --- SOFT DELETE ---
    async def delete_user(self, user_id: UUID) -> None:
        logger.info(f"Soft deleting user UUID: {user_id}")
        async with self.uow:
            user = await self.uow.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
                
            # Вместо удаления проставляем дату удаления
            user.deleted_at = datetime.now(timezone.utc)
            await self.uow.commit()

