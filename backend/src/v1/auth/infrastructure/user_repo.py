import logging

from sqlalchemy import String, cast, select

from backend.core.db.postgres.data_orms.role_orm import Role
from backend.core.db.postgres.data_orms.user_orm import User
from backend.src.v1.auth.domain.interfaces import IUserRepo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.auth.presentation.dto.user_dto import UserCreateDTO, UserResponseDTO

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


    async def create_user(self, user: UserCreateDTO) -> UserResponseDTO:
        """Создает пользователя из UserCreate DTO и возвращает UserModel"""
        logger.info(f"Creating user: email={user.email}, username={user.username}")
        user_orm = User(
            email=user.email,
            pwdhash=user.password,
            username=user.username,
            role_id=2
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
        logger.info(f"User created successfully: id={result.id}, email={result.email}")
        return result

    async def get_role(self, user_id: str):
        stmt = select(Role.name).join(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def update_user_by_id(self, user_id: str) -> User:
        return User()

    async def delete_user_by_id(self, user_id: str) -> None:
        return