from backend.src.v1.data.domain.interfaces import IWorkRepo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.data.presentation.dtos.work_dto import WorkCreateResponse, WorkDeleteResponse, WorkResponse, WorkUpdateResponse, WorksResponse

class PgWorkRepo(IWorkRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session


    async def get_works(self) -> WorksResponse:
        pass

    async def get_work(self, work_id: int) -> WorkResponse:
        pass

    async def create_work(self) -> WorkCreateResponse:
        pass

    async def update_work(self) -> WorkUpdateResponse:
        pass

    async def delete_work(self) -> WorkDeleteResponse:
        pass