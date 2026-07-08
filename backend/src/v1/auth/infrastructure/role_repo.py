import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.db.postgres.data_orms.role_orm import Permission, Role
from backend.src.v1.auth.domain.interfaces import IRoleRepo
from backend.src.v1.auth.presentation.dto.role_dto import PermissionCreate, RoleCreateRequest, RoleCreateResponse
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest

logger = logging.getLogger(__file__)

class PgRoleRepo(IRoleRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        return await self.session.get(Role, role_id)

    async def get_by_id_with_permissions(self, role_id: int) -> Optional[Role]:
        stmt = (
            select(Role)
            .where(Role.id == role_id)
            .options(selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Role]:
        stmt = (
            select(Role)
            .where(Role.name == name)
            .options(selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Role]:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .order_by(Role.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, role: Role) -> None:
        self.session.add(role)

    async def delete(self, role: Role) -> None:
        await self.session.delete(role)