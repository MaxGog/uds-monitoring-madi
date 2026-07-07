from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import ITaskRepo, ITaskUsecases
from backend.src.v1.data.presentation.dtos.task_dto import TaskCreateResponse, TaskDeleteResponse, TaskResponse, TaskUpdateResponse, TasksResponse


@dataclass
class TaskUsecases(ITaskUsecases):
    uow: IUnitOfWork
    task_repo: ITaskRepo
    user_repo: IUserRepo

    async def get_tasks(self) -> TaskResponse:
        pass

    async def get_task(self, data: dict) -> TasksResponse:
        pass

    async def create_task(self, data: dict) -> TaskCreateResponse:
        pass

    async def update_task(self, data: dict) -> TaskUpdateResponse:
        pass

    async def delete_task(self, data: dict) -> TaskDeleteResponse:
        pass