import logging

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List, Optional

from backend.core.db.postgres.data_orms.role_orm import Permission
from backend.src.v1.auth.domain.interfaces import IPermissionRepo
from backend.src.v1.auth.domain.role_models import ActionType, EntityType

logger = logging.getLogger(__file__)

class PgPermissionRepo(IPermissionRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_ids(self, ids: List[int]) -> List[Permission]:
        if not ids:
            return []
        stmt = select(Permission).where(Permission.id.in_(ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_entity_and_action(self, entity: EntityType, action: ActionType) -> Optional[Permission]:
        """Найти разрешение по уникальной паре (entity, action)"""
        stmt = select(Permission).where(
            Permission.entity == entity,
            Permission.action == action
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, entity: EntityType, action: ActionType) -> Permission:
        """Создать новое разрешение в БД"""
        permission = Permission(entity=entity, action=action)
        self.session.add(permission)
        await self.session.flush()
        return permission
    
    async def add(self, permission: Permission) -> None:
        self.session.add(permission)

    async def delete_by_entity_and_action(self, entity, action) -> None:
        stmt = delete(Permission).where(Permission.entity == entity, Permission.action == action)
        await self.session.execute(stmt)