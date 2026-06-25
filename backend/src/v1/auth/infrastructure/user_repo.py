import logging

from sqlalchemy import select

from backend.core.db.postgres.orm import User
from backend.src.v1.auth.domain.interfaces import IUserRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger('UserRepo')

class PGUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        pass
    
    async def get_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        logger.debug("Looking for username match")
        result = await self.session.execute(stmt)
        logger.debug(f"Found: {result}")
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == int(user_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        """Создает пользователя из UserCreate DTO и возвращает UserEntity"""
        logger.info(f"Creating user: email={user.email}, username={user.username}")
        user_orm = User(
            email=user.email,
            pwdhash=user.password,
            username=user.username
        )
        logger.debug(f"UserORM instance created: {user_orm}")
        self.session.add(user_orm)
        logger.debug("User added to session")
        
        await self.session.flush()
        logger.debug("Session flushed successfully")

        result = User(
            id=user_orm.id,
            email=user_orm.email,
            username=user_orm.username,
            password_hash_bytes=user_orm.pwdhash
        )
        logger.info(f"User created successfully: id={result.id}, email={result.email}")
        return result


    async def update_user_by_id(self, user_id: str) -> User:
        pass

    async def delete_user_by_id(self, user_id: str) -> None:
        pass