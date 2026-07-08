from dataclasses import dataclass

from fastapi import HTTPException, status

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IRoleRepo, IRoleUsecases, IUserRepo
from backend.src.v1.auth.presentation.dto.role_dto import RoleCreateRequest, RoleCreateResponse
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest


@dataclass
class RoleUsecases(IRoleUsecases):
    uow: IUnitOfWork
    user_repo: IUserRepo
    role_repo: IRoleRepo

    async def get_role(self):
        pass

    async def get_roles(self):
        pass

    async def create_role(self, data: RoleCreateRequest) -> RoleCreateResponse:
        async with self.uow as uow:
            result = await uow.role_repo.create_role(data)
            if not result:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            await self.uow.commit()
        return result

    async def create_permission(self, data):
        async with self.uow as uow:
            result = await uow.role_repo.create_permission(data)
            if not result:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            return result

    async def update_role(self):
        pass

    async def delete_role(self):
        pass
