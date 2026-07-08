from dataclasses import dataclass

from fastapi import HTTPException, status

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.auth.domain.role_models import RoleName
from backend.src.v1.data.domain.interfaces import ITaskRepo, ITaskUsecases
from backend.src.v1.data.presentation.dtos.task_dto import TaskCreateResponse, TaskDeleteResponse, TaskResponse, TaskUpdateResponse, TasksResponse


@dataclass
class TaskUsecases(ITaskUsecases):
    uow: IUnitOfWork
    task_repo: ITaskRepo
    user_repo: IUserRepo

    async def get_tasks(self, user_id: str,) -> TaskResponse:
        role = await self.user_repo.get_role(user_id)

        if role not in (RoleName.VIEWER, RoleName.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        # Выполнить проверку прав доступа для кастомной роли

        return await self.task_repo.get_tasks()

    async def get_task(self, user_id: str, data: dict) -> TasksResponse:
        role = await self.user_repo.get_role(user_id)

        if role not in (RoleName.VIEWER, RoleName.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        # Выполнить проверку прав доступа для кастомной роли

        return await self.task_repo.get_task(data['task_id'])

    async def create_task(self, user_id: str, data: dict) -> TaskCreateResponse:
        role = await self.user_repo.get_role(user_id)

        if role is not RoleName.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        return await self.task_repo.create_task()

    async def update_task(self, user_id: str, data: dict) -> TaskUpdateResponse:
        role = await self.user_repo.get_role(user_id)

        if role is not RoleName.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        return await self.task_repo.update_task()

    async def delete_task(self, user_id: str, data: dict) -> TaskDeleteResponse:
        role = await self.user_repo.get_role(user_id)

        if role is not RoleName.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        return await self.task_repo.delete_task()