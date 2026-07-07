import logging

from fastapi import HTTPException, status
from sqlalchemy import String, cast, select

from backend.core.db.postgres.data_orms.role_orm import Role
from backend.core.db.postgres.data_orms.user_orm import User
from backend.src.v1.auth.domain.interfaces import IUserRepo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest, BaseResponse, UserCreateDTO, UserResponseDTO

logger = logging.getLogger('UserRepo')

class PGUserRepo(IUserRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_by_email(self, email: str) -> UserResponseDTO | None:
        logger.info("Getting user by email")
        stmt = select(User).where(User.email == email)
        logger.debug("Looking for email match")
        result = await self.session.execute(stmt)
        logger.debug(f"Found: {result}")
        return result.unique().scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        logger.debug("Looking for username match")
        result = await self.session.execute(stmt)
        logger.debug(f"Found: {result}")
        return result.unique().scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        stmt = select(User).where(User.id == str(user_id))
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_all(self, limit: int, offset: int) -> list[User] | None:
        logger.info('Getting all users')
        stmt = (
            select(
            cast(User.id, String).label("id"),
            User.username,
            User.email,
            Role.name.label('role')
            )
        .join(Role, User.role_id == Role.id)
        .limit(limit)
        .offset(offset)
        )
        logger.debug('Looking for all users')
        result = await self.session.execute(stmt)
        return result.mappings().all() # type: ignore


    async def create_user(self, data: BaseRequest[UserCreateDTO]) -> BaseResponse[UserResponseDTO]:
        """Создает пользователя из UserCreate DTO и возвращает UserModel"""
        try :
            logger.info(f"Creating user: email={data.data.email}, username={data.data.username}")
            role_id = None
            print(data.data.role)
            logger.info(data.data.role)
            if data.data.role:
                role_id = await self.get_role_by_name(data.data.role)
            if role_id is None:
                logger.warning("Роль не найдена, пользователь будет без прав")
            user_orm = User(
                email=data.data.email,
                pwdhash=data.data.password,
                username=data.data.username,
                role_id = role_id,
                full_name = data.data.full_name,
                company_id = data.data.company_id,
                position = data.data.position,
            )
            logger.debug(f"UserORM instance created: {user_orm}")
            self.session.add(user_orm)
            logger.debug("User added to session")
            
            await self.session.flush()
            logger.debug("Session flushed successfully")

            result = UserResponseDTO(
                id=str(user_orm.id),
                email=user_orm.email,  # type: ignore
                username=user_orm.username,
                
            )
            await self.session.commit()
            logger.info(f"User created successfully: id={result.id}, email={result.email}, role = {result.role}")
            return BaseResponse(data = result)
        except Exception as e:
            logger.error(e)
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

    async def update_user_by_id(self, user_id: str) -> User:
        return User()

    async def delete_user_by_id(self, user_id: str) -> None:
        return