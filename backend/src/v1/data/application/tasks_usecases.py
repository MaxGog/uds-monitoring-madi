from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from typing import List

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.task_orm import Task
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import ITaskRepo, ITaskUsecases
from backend.src.v1.data.domain.models import TaskStatus
from backend.src.v1.data.presentation.dtos.task_dto import TaskCreateRequest, TaskResponse, TaskUpdateRequest

logger = logging.getLogger(__file__)


class TaskUsecases(ITaskUsecases):
    uow: IUnitOfWork
    task_repo: ITaskRepo
    user_repo: IUserRepo

    async def get_tasks(self) -> List[TaskResponse]:
        tasks = await self.task_repo.get_all()
        return [TaskResponse.model_validate(r) for r in tasks]

    async def get_task_by_id(self, item_id: int) -> TaskResponse:
        task = await self.task_repo.get_by_id(item_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return TaskResponse.model_validate(task)

    async def create_task(self, author_id: str, data: TaskCreateRequest) -> TaskResponse:
        async with self.uow as uow:
            # Если задачу создали выполненной
            completed_at = datetime.now(timezone.utc) if data.status == TaskStatus.COMPLETED else None
            # Задачи могут повторяться по всем полям, кроме id. Валидации не проводим.
            new_task = Task(
                title=data.title,
                description=data.description,
                status=data.status,
                priority=data.priority,
                author_id=author_id,
                completed_at=completed_at,
                performers=[]
            )
            # Если переданы исполнители
            if data.performer_ids:
                for user_id in data.performer_ids:
                    performer = await self.uow.users.get_by_id(user_id)
                    if not performer:
                        raise HTTPException(status_code=400, detail=f"Performer with id {user_id} not found")
                    new_task.performers.append(performer)

            await uow.task_repo.add(new_task)
            await uow.commit()
            
            task_with_relations = await self.uow.task_repo.get_by_id_with_relations(new_task.id)
            return TaskResponse.model_validate(task_with_relations)

    async def update_task(self, item_id: int, data: TaskUpdateRequest) -> TaskResponse:
        logger.info(f"Patching task_id: {item_id}")
        
        async with self.uow:
            task = await self.uow.task_repo.get_by_id_with_relations(item_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                return TaskResponse.model_validate(task)

            # Логика completed_at при смене статуса
            if "status" in update_data:
                new_status = update_data["status"]
                if new_status == TaskStatus.COMPLETED and task.status != TaskStatus.COMPLETED:
                    task.completed_at = datetime.now(timezone.utc)
                elif new_status != TaskStatus.COMPLETED and task.status == TaskStatus.COMPLETED:
                    task.completed_at = None

            # Логика обновления Many-to-Many списка исполнителей
            if "performer_ids" in update_data:
                new_performer_ids = update_data.pop("performer_ids")
                task.performers.clear()
                
                if new_performer_ids:
                    for user_id in new_performer_ids:
                        performer = await self.uow.users.get_by_id(user_id)
                        if not performer:
                            raise HTTPException(status_code=400, detail=f"Performer {user_id} not found")
                        task.performers.append(performer)

            # Обновление остальных дефолтных полей
            for key, value in update_data.items():
                setattr(task, key, value)

            await self.uow.commit()
            
            # Обновляем состояние объекта в памяти перед маппингом
            task = await self.uow.task_repo.get_by_id_with_relations(item_id)
            return TaskResponse.model_validate(task)

    async def delete_task(self, item_id: int) -> None:
        logger.info(f"Deleting task by id: {item_id}")
        
        async with self.uow as uow:
            task = await uow.task_repo.get_by_id(item_id)
            if not task:
                raise HTTPException(status_code=404, detail="task not found")

            await uow.task_repo.delete(task)
            await uow.commit()