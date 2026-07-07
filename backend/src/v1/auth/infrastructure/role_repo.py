import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.auth.domain.interfaces import IRoleRepo

logger = logging.getLogger(__file__)

class PGRoleRepo(IRoleRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_roles(self,):
        pass

    async def get_role(self, data):
        pass

    async def create_role(self, data):
        pass

    async def update_role(self, data):
        pass

    async def delete_role(self, data):
        pass

    async def create_permission(self, data):
        pass

    async def delete_permission(self, data):
        pass

    async def get_role_permissions(self, data):
        pass