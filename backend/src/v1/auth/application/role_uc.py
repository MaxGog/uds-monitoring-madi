from dataclasses import dataclass
import logging
from typing import List

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.role_orm import Role
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IRoleRepo, IRoleUsecases, IUserRepo
from backend.src.v1.auth.presentation.dto.role_dto import RoleCreateRequest, RoleResponse, RoleUpdateRequest

logger = logging.getLogger(__file__)

@dataclass
class RoleUsecases(IRoleUsecases):
    uow: IUnitOfWork
    user_repo: IUserRepo
    role_repo: IRoleRepo

    async def create_role(self, data: RoleCreateRequest) -> RoleResponse:
        logger.info(f"Creating system role: {data.name}")
        
        async with self.uow as uow:
            # 1. Проверяем уникальность имени
            existing_role = await uow.role_repo.get_by_name(data.name)
            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Role with name '{data.name}' already exists"
                )

            # 2. Вытягиваем сущности прав из БД для M2M связывания
            permissions_to_bind = []
            if data.permission_ids:
                permissions_to_bind = await uow.permission_repo.get_by_ids(data.permission_ids)
                if len(permissions_to_bind) != len(set(data.permission_ids)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="One or more permission IDs are invalid"
                    )

            # 3. Сохраняем роль
            new_role = Role(
                name=data.name,
                scope=data.scope,
                permissions=permissions_to_bind
            )
            
            await uow.role_repo.add(new_role)
            await uow.commit()
            
            # Обновляем состояние объекта из базы данных
            role = await uow.role_repo.get_by_id(new_role.id)
            return RoleResponse.model_validate(role)

    # --- READ (SINGLE) ---
    async def get_role_by_id(self, item_id: int) -> RoleResponse:
        role = await self.role_repo.get_by_id(item_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return RoleResponse.model_validate(role)

    # --- READ (LIST) ---
    async def get_all_roles(self) -> List[RoleResponse]:
        roles = await self.role_repo.get_all()
        return [RoleResponse.model_validate(r) for r in roles]

    # --- UPDATE (PATCH) ---
    async def update_role(self, item_id: int, data: RoleUpdateRequest) -> RoleResponse:
        logger.info(f"Patching role ID: {item_id}")
        
        async with self.uow as uow:
            role = await uow.role_repo.get_by_id(item_id)
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")

            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                return RoleResponse.model_validate(role)

            # Проверяем уникальность имени, если оно меняется
            if "name" in update_data and update_data["name"] != role.name:
                existing = await uow.role_repo.get_by_name(update_data["name"])
                if existing:
                    raise HTTPException(status_code=400, detail="Role name must be unique")

            # Перезапись Many-to-Many связей (прав доступа)
            if "permission_ids" in update_data:
                new_perm_ids = update_data.pop("permission_ids")
                if new_perm_ids is not None:
                    db_permissions = await uow.permission_repo.get_by_ids(new_perm_ids)
                    if len(db_permissions) != len(set(new_perm_ids)):
                        raise HTTPException(status_code=400, detail="Invalid permission IDs detected")
                    
                    # Прямая мутация списка перезапишет записи в ассоциативной таблице role_permissions
                    role.permissions = db_permissions

            # Обновление остальных полей (name, scope)
            for key, value in update_data.items():
                setattr(role, key, value)

            await uow.commit()
            
            # Перечитываем актуальный стейт
            role = await uow.role_repo.get_by_id(item_id)
            return RoleResponse.model_validate(role)

    # --- DELETE ---
    async def delete_role(self, item_id: int) -> None:
        logger.info(f"Deleting role ID: {item_id}")
        async with self.uow as uow:
            role = await uow.role_repo.get_by_id(item_id)
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")

            # Предохранитель: проверяем, не привязана ли роль к живым пользователям
            users_with_role = await uow.user_repo.count_by_role(item_id)
            if users_with_role > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete role. It is currently assigned to {users_with_role} users."
                )

            # Благодаря ondelete="CASCADE" в таблице линковки,
            # записи из role_permissions удалятся автоматически на уровне БД.
            await uow.role_repo.delete(role)
            await uow.commit()
