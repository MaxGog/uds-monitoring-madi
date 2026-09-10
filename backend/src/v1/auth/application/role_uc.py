from dataclasses import dataclass
import logging
from typing import List

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.role_orm import Permission, Role
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IPermissionRepo, IRoleRepo, IRoleUsecases, IUserRepo
from backend.src.v1.auth.presentation.dto.role_dto import PermissionCreateRequest, RoleCreateRequest, RoleResponse, RoleUpdateRequest

logger = logging.getLogger(__file__)

@dataclass
class RoleUsecases(IRoleUsecases):
    uow: IUnitOfWork
    user_repo: IUserRepo
    role_repo: IRoleRepo
    perm_repo: IPermissionRepo

    async def create_role(self, data: RoleCreateRequest) -> RoleResponse:
        logger.info(f"Creating system role: {data.name}")
        try:
            async with self.uow as uow:
                # 1. Проверяем уникальность имени
                existing_role = await uow.role_repo.get_by_name(data.name)
                if existing_role:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail=f"Role with name '{data.name}' already exists"
                    )

                permissions_to_bind = []
                if data.permissions:
                    permissions_to_bind = await self._resolve_permissions(uow, data.permissions)

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
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise e
    
    # --- READ (SINGLE) ---
    async def get_role_by_id(self, item_id: int) -> RoleResponse:
        try:
            role = await self.role_repo.get_by_id(item_id)
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")
            return RoleResponse.model_validate(role)
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise e

    # --- READ (LIST) ---
    async def get_all_roles(self) -> List[RoleResponse]:
        try:
            roles = await self.role_repo.get_all()
            return [RoleResponse.model_validate(r) for r in roles]
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise e

    # --- UPDATE (PATCH) ---
    async def update_role(self, item_id: int, data: RoleUpdateRequest) -> RoleResponse:
        logger.info(f"Patching role ID: {item_id}")
        try:
            async with self.uow as uow:
                role = await uow.role_repo.get_by_id(item_id)
                if not role:
                    raise HTTPException(status_code=404, detail="Role not found")

                update_data = data.model_dump(exclude_unset=True, exclude_none=True)
                if not update_data:
                    return RoleResponse.model_validate(role)

                # Проверяем уникальность имени, если оно меняется
                if "name" in update_data and update_data["name"] != role.name:
                    existing = await uow.role_repo.get_by_name(update_data["name"])
                    if existing:
                        raise HTTPException(status_code=400, detail="Role name must be unique")
                    
                resolved_permissions = None
                if 'permissions' in update_data:
                    resolved_permissions = await self._resolve_permissions(uow, update_data['permissions'])
                    role.permissions = resolved_permissions
                    del update_data["permissions"]

                for key, value in update_data.items():
                    setattr(role, key, value)

                await uow.commit()

                role = await uow.role_repo.get_by_id(item_id)
                return RoleResponse.model_validate(role)
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise e
        
    # --- DELETE ---
    async def delete_role(self, item_id: int) -> None:
        logger.info(f"Deleting role ID: {item_id}")
        try:
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

                # ondelete="CASCADE" в таблице линковки,
                # записи из role_permissions удалятся автоматически на уровне БД.
                await uow.role_repo.delete(role)
                await uow.commit()
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise e
        
    async def _resolve_permissions(self, uow: IUnitOfWork, permissions: List[int | PermissionCreateRequest]) -> list[Permission]:
        """Внутренний хелпер для get-or-create логики разрешений через репозиторий"""
        try:
            resolved_permissions: list[Permission] = []
            permission_ids = [p for p in permissions if isinstance(p, int)]
            permission_schemas = [p for p in permissions if isinstance(p, PermissionCreateRequest)]
            
            # Шаг А: Получаем существующие пермишены по ID
            if permission_ids:
                existing_perms = await uow.permission_repo.get_by_ids(permission_ids)
                if len(existing_perms) != len(permission_ids):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Один или несколько указанных ID прав доступа не существуют в системе."
                    )
                resolved_permissions.extend(existing_perms)
                
            # Шаг Б: Логика Get-or-Create для динамических схем
            for schema in permission_schemas:
                perm = await uow.permission_repo.get_by_entity_and_action(schema.entity, schema.action)
                if not perm:
                    perm = await uow.permission_repo.create(entity=schema.entity, action=schema.action)
                resolved_permissions.append(perm)
                
            return resolved_permissions
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise e