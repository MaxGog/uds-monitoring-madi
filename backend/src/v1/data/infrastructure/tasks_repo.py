from backend.src.v1.data.domain.interfaces import ITaskRepo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.data.presentation.dtos.task_dto import TaskCreateResponse, TaskDeleteResponse, TaskResponse, TaskUpdateResponse, TasksResponse

class PgTaskRepo(ITaskRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_tasks(self) -> TasksResponse:
        pass

    async def get_task(self, task_id: int) -> TaskResponse:
        pass

    async def create_task(self) -> TaskCreateResponse:
        pass

    async def update_task(self) -> TaskUpdateResponse:
        pass

    async def delete_task(self) -> TaskDeleteResponse:
        pass