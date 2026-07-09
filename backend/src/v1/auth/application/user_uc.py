from dataclasses import dataclass
import logging
from typing import List
from uuid import UUID

from fastapi import HTTPException, status

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IPasswordHasher, IUserRepo, IUserUsecases
from backend.src.v1.auth.presentation.dto.user_dto import UserCreateRequest, UserDeleteRequest, UserResponse, UserUpdateRequest

logger = logging.getLogger(__file__)

@dataclass
class UserUsecases(IUserUsecases):
    uow: IUnitOfWork
    hasher: IPasswordHasher
    user_repo: IUserRepo

    async def get_me(self, user_id) -> UserResponse:
        result = await self.user_repo.get_by_id(user_id)
        response = UserResponse(
            id = str(result.id),
            username = result.username,
            email = result.email,
            full_name = result.full_name,
            role = str(result.role.name),
            company = result.company,
            position = result.position,
            status = result.status
        )
        return response

    async def get_users(self, user_id: str, limit: int = 20, offset: int = 0) -> List[UserResponse]:
        role = await self.user_repo.get_role(user_id)
        
        return await self.user_repo.get_all(limit = limit, offset = offset)
    
    async def create_user(self, creator_id: str, data: UserCreateRequest, ) -> UserResponse:
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise HTTPException(status_code=409, detail='username or email already exists')
        password_hash_str = self.hasher.hash_password(data.password)
        data.password = password_hash_str
        user = await self.user_repo.create_user(data)
        return user
    
    async def update_user(self, user_id: str, data: UserUpdateRequest) -> UserResponse:
        try:
            async with self.uow as uow:
                user = await self.user_repo.get_by_id(user_id)
                if not user:
                    logger.warning(f"User with id={user_id} not found for update")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )
                
                update_data = data.model_dump(exclude_unset=True)
                if not update_data:
                    logger.debug("No fields provided for update, returning current state")
                    return self._to_response_dto(user)
                
                for key, value in update_data.items():
                    setattr(user, key, value)
                    logger.debug(f"Field '{key}' updated to '{value}' in-memory")

                await self.user_repo.flush()
                
                if "role_id" in update_data or "company_id" in update_data:
                    user = await self.user_repo.get_by_id(user_id)

                logger.info(f"User {user_id} successfully updated in database")
                await uow.commit()
                return self._to_response_dto(user)
        except Exception as e:
            logger.error(e)

    async def delete_user(self, user_id: str, data: UserDeleteRequest) -> UserResponse:
        try:
            async with self.uow as uow:
                user = await self.user_repo.delete_user_by_id(user_id)
                user = await self.user_repo.get_by_id(user_id)
                if not user:
                    logger.warning(f"User with id={user_id} not found for update")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )
                return self._to_response_dto(user)
        except Exception as e:
            logger.error(e)

    def _to_response_dto(self, user_orm) -> UserResponse:
        """Маппинг ORM модели в чистый Pydantic DTO"""
        return UserResponse(
            id=str(user_orm.id),
            email=user_orm.email,
            username=user_orm.username,
            role=user_orm.role_name,
            company=user_orm.company_name,
            full_name=user_orm.full_name,
            position=user_orm.position,
            status=user_orm.status,
        )

