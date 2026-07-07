from backend.src.v1.data.domain.interfaces import IObjectRepo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.data.presentation.dtos.object_dto import ObjectCreateResponse, ObjectDeleteResponse, ObjectResponse, ObjectUpdateResponse, ObjectsResponse

class PgObjectRepo(IObjectRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session


    async def get_objects(self) -> ObjectsResponse:
        pass

    async def get_object(self, object_id: int) -> ObjectResponse:
        pass

    async def create_object(self) -> ObjectCreateResponse:
        pass

    async def update_object(self) -> ObjectUpdateResponse:
        pass

    async def delete_object(self) -> ObjectDeleteResponse:
        pass