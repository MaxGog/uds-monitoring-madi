from datetime import datetime, timezone
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Null, String, cast, delete, func, select, update

from backend.core.db.postgres.data_orms.user_orm import User
from backend.src.v1.auth.domain.interfaces import IUserRepo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

logger = logging.getLogger('UserRepo')

class PgUserRepo(IUserRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.id == user_id, User.deleted_at.is_(None))
            .options(joinedload(User.company))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[User]:
        stmt = (
            select(User)
            .where(User.deleted_at.is_(None))
            .options(joinedload(User.company))
            .order_by(User.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_company(self, item_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(User.company_id == item_id, User.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_by_role(self, item_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(User.role_id == item_id, User.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def hard_delete_by_email(self, email: str) -> None:
        try:
            stmt = (
                delete(User).where(User.email == email)
            )
            await self.session.execute(stmt)
            return
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail = 'Error deleting user by email')

    async def add(self, user: User) -> None:
        self.session.add(user)