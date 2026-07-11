import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from backend.core.db.postgres.data_orms.role_orm import Permission
from backend.src.v1.auth.domain.interfaces import IPermissionRepo
from backend.src.v1.auth.domain.role_models import EntityType

logger = logging.getLogger(__file__)

class PgPermissionRepo(IPermissionRepo):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_ids(self, ids: List[int]) -> List[Permission]:
        if not ids:
            return []
        stmt = select(Permission).where(Permission.id.in_(ids))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_names(self, names: List[EntityType]) -> List[Permission]:
        pass