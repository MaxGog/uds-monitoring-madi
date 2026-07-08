import logging

from fastapi import HTTPException, status
from sqlalchemy import Null, String, cast, func, select, update

from backend.core.db.postgres.data_orms.copmany_orm import Company
from backend.core.db.postgres.data_orms.role_orm import Role
from backend.core.db.postgres.data_orms.user_orm import User
from backend.src.v1.auth.domain.interfaces import IUserRepo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from backend.src.v1.auth.domain.models import UserStatus
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest, BaseResponse, UserCreateRequest, UserDeleteRequest, UserResponse, UserRestoreRequest, UserUpdateRequest

logger = logging.getLogger('UserRepo')

class PgUserRepo(IUserRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def flush(self) -> None:
        await self.session.flush()

    async def get_by_email(self, email: str) -> User | None:
        logger.info("Getting user by email")
        stmt = select(User).where(User.email == email)
        logger.debug("Looking for email match")
        result = await self.session.execute(stmt)
        logger.debug(f"Found: {result}")
        return result.unique().scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        logger.debug("Looking for username match")
        result = await self.session.execute(stmt)
        logger.debug(f"Found: {result}")
        return result.unique().scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        try:
            stmt = select(User).where(User.id == str(user_id))
            result = await self.session.execute(stmt)
            return result.unique().scalar_one_or_none()
        except Exception as e:
            logger.error(e)

    async def get_all(self, limit: int, offset: int) -> list[User] | None:
        logger.info('Getting all users')
        stmt = (
            select(
            cast(User.id, String).label("id"),
            User.username,
            User.email,
            User.full_name,
            User.position,
            Role.name.label('role'),
            Company.name.label('company'),
            User.status,
            )
        .join(Role, User.role_id == Role.id)
        .join(Company, User.company_id == Company.id, isouter=True)
        .limit(limit)
        .offset(offset)
        )
        logger.debug('Looking for all users')
        result = await self.session.execute(stmt)
        return result.mappings().all() # type: ignore

    async def create_user(self, data: UserCreateRequest) -> UserResponse | None:
        """Создает пользователя из UserCreate DTO и возвращает UserResponse"""
        try :
            logger.info(f"Creating user: email={data.email}, username={data.username}")
            role_id = None

            if data.role:
                role_id = await self.get_role_id_by_name(data.role)

            if role_id is None:
                logger.warning("Роль не найдена, пользователь будет без прав")

            user_orm = User(
                email=data.email,
                pwdhash=data.password,
                username=data.username,
                role_id = role_id,
                full_name = data.full_name,
                company_id = data.company_id,
                position = data.position,
            )

            self.session.add(user_orm)
            logger.debug("User added to session")
            
            await self.session.flush()
            logger.debug("Session flushed successfully")

            stmt = (
                select(User)
                .where(User.id == user_orm.id)
                .options(
                    joinedload(User.role),
                    joinedload(User.company),
                )
            )
            result_set = await self.session.execute(stmt)
            user_orm = result_set.scalar_one()

            result = UserResponse(
                id=str(user_orm.id),
                email = user_orm.email,  # type: ignore
                username = user_orm.username,
                role = user_orm.role_name,
                full_name = user_orm.full_name,
                company = user_orm.company_name,
                position = user_orm.position,
                status = user_orm.status,
            )
            print(result)
            await self.session.commit()
            logger.info(f"User created successfully: id={result.id}, email={result.email}, role = {result.role}")

            return result
        except Exception as e:
            logger.error(e)
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def get_role(self, user_id: str):
        stmt = select(Role.name).join(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_role_name_by_id(self, role_id: int):
        stmt = select(Role.name).where(Role.id == role_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_role_id_by_name(self, role_name: str) -> int | None:
        stmt = select(Role.id).where(Role.name == role_name)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def update_user_by_id(self, data: UserUpdateRequest) -> User | None:
        """Обновляет данные пользователя."""
        try:
            stmt = select(User).where(User.id == data.id)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                return None

            update_data = data.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error updating user {data.id}: {e}")
            raise

    async def delete_user_by_id(self, data: UserDeleteRequest) -> bool:
        '''
        Для сохранения истории в компании юзеры будут удаляться мягко.
        '''
        try:
            stmt = update(User).where(User.id == data.user_id).values(deleted_at=func.now(), status = UserStatus.BLOCKED)
            await self.session.execute(stmt)
            await self.session.commit()
            return True
        except Exception as e:
            logger.error(e)
            await self.session.rollback()
            return False
        
    async def restore_user_by_id(self, data: BaseRequest[UserRestoreRequest]) -> bool:
        '''
        Для восстановления мягко удаленного юзера.
        '''
        try:
            stmt = update(User).where(User.id == data.data.user_id).values(deleted_at=Null, status = UserStatus.ACTIVE)
            await self.session.execute(stmt)
            await self.session.commit()
            return True
        except Exception as e:
            logger.error(e)
            await self.session.rollback()
            return False