import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db.postgres.data_orms.role_orm import Permission, Role
from backend.src.v1.auth.domain.interfaces import IRoleRepo
from backend.src.v1.auth.presentation.dto.role_dto import PermissionCreate, RoleCreateRequest, RoleCreateResponse
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest

logger = logging.getLogger(__file__)

class PgRoleRepo(IRoleRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_roles(self,) -> list[Role] | None:
        try:
            pass
        except Exception as e:
            logger.error(e)

    async def get_role(self, data) -> Role | None:
        try:
            pass
        except Exception as e:
            logger.error(e)

    async def create_role(self, data: RoleCreateRequest) -> RoleCreateResponse:
        try:
            new_role = Role(
                name=data.name,
                scope=data.scope,
                permissions=[
                    Permission(entity=p.entity, action=p.action) 
                    for p in data.permissions
                ]
            )

            self.session.add(new_role)
            await self.session.flush()
            await self.session.refresh(new_role)
            return RoleCreateResponse(
                id=new_role.id,
                name=new_role.name,
                scope=new_role.scope,
                permissions=[
                    PermissionCreate(entity=p.entity, action=p.action) 
                    for p in new_role.permissions
                ]
            )
        except Exception as e:
            logger.error(e)

    async def update_role(self, data) -> Role:
        try:
            pass
        except Exception as e:
            logger.error(e)

    async def delete_role(self, data) -> bool:
        try:
            pass
        except Exception as e:
            logger.error(e)

    async def create_permission(self, data) -> Permission:
        try:
            pass
        except Exception as e:
            logger.error(e)

    async def delete_permission(self, data) -> bool:
        try:
            pass
        except Exception as e:
            logger.error(e)

    async def get_role_permissions(self, data):
        try:
            pass
        except Exception as e:
            logger.error(e)