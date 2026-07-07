from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IWorkRepo, IWorkUsecases
from backend.src.v1.data.presentation.dtos.work_dto import WorkCreateResponse, WorkDeleteResponse, WorkResponse, WorkUpdateResponse, WorksResponse


@dataclass
class WorkUsecases(IWorkUsecases):
    uow: IUnitOfWork
    work_repo: IWorkRepo
    user_repo: IUserRepo

    async def get_works(self) -> WorkResponse:
        pass

    async def get_work(self, data: dict) -> WorksResponse:
        pass

    async def create_work(self, data: dict) -> WorkCreateResponse:
        pass

    async def update_work(self, data: dict) -> WorkUpdateResponse:
        pass

    async def delete_work(self, data: dict) -> WorkDeleteResponse:
        pass  