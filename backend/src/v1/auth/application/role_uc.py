from dataclasses import dataclass
import logging
from typing import List

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.role_orm import Permission, Role
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IRoleRepo, IRoleUsecases, IUserRepo
from backend.src.v1.auth.presentation.dto.role_dto import RoleCreateRequest, RoleCreateResponse, RoleResponse, RoleUpdateRequest
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest

logger = logging.getLogger(__file__)

@dataclass
class RoleUsecases(IRoleUsecases):
    uow: IUnitOfWork
    user_repo: IUserRepo
    role_repo: IRoleRepo

    async def get_role_by_id(self, role_id: int) -> RoleResponse:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return RoleResponse.model_validate(role)

    async def get_all_roles(self) -> List[RoleResponse]:
        roles = await self.role_repo.get_all()
        return [RoleResponse.model_validate(r) for r in roles]

    async def create_role(self, data: RoleCreateRequest) -> RoleResponse:
        async with self.uow as uow:
            existing_role = await uow.role_repo.get_by_name(data.name.upper())
            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role '{data.name}' already exists"
                )

            orm_permissions = [
                Permission(entity=p.entity, action=p.action) 
                for p in data.permissions
            ]

            new_role = Role(
                name=data.name.upper(),
                scope=data.scope,
                permissions=orm_permissions
            )
            
            await uow.role_repo.add(new_role)
            await uow.commit()
            
            return RoleResponse.model_validate(new_role)

    async def create_permission(self, data):
        async with self.uow as uow:
            result = await uow.role_repo.create_permission(data)
            if not result:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            return result

    async def update_role(self, role_id: int, data: RoleUpdateRequest) -> RoleResponse:
        logger.info(f"Patching role_id: {role_id}")
        
        async with self.uow as uow:
            role = await uow.role_repo.get_by_id_with_permissions(role_id)
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")

            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                return RoleResponse.model_validate(role)

            if "name" in update_data:
                new_name = update_data["name"].upper()
                if new_name != role.name:
                    existing_role = await uow.role_repo.get_by_name(new_name)
                    if existing_role:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Role '{new_name}' already exists"
                        )
                update_data["name"] = new_name

            if "permissions" in update_data:
                # Полная перезапись всех прав. [] = нет прав
                new_perms = update_data.pop("permissions")
                role.permissions = [
                    Permission(entity=p.entity, action=p.action) 
                    for p in new_perms
                ]

            for key, value in update_data.items():
                setattr(role, key, value)

            await uow.commit()

            role = await uow.role_repo.get_by_id_with_permissions(role_id)
            return RoleResponse.model_validate(role)

    async def delete_role(self, role_id: int) -> None:
        logger.info(f"Deleting role_id: {role_id}")
        
        async with self.uow as uow:
            role = await uow.role_repo.get_by_id(role_id)
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")
                
            # Защита: проверяем, нет ли пользователей с этой ролью перед удалением
            user_count = await uow.users.count_by_role(role_id)
            if user_count > 0:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot delete role: it is assigned to existing users"
                )

            await uow.role_repo.delete(role)
            await uow.commit()
