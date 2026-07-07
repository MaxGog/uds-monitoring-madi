from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IObjectRepo, IObjectUsecases
from backend.src.v1.data.presentation.dtos.object_dto import ObjectCreateResponse, ObjectDeleteResponse, ObjectResponse, ObjectUpdateResponse, ObjectsResponse


@dataclass
class ObjectUsecases(IObjectUsecases):
    uow: IUnitOfWork
    object_repo: IObjectRepo
    user_repo: IUserRepo

    async def get_objects(self) -> ObjectResponse:
        pass

    async def get_object(self, data: dict) -> ObjectsResponse:
        pass

    async def create_object(self, data: dict) -> ObjectCreateResponse:
        pass

    async def update_object(self, data: dict) -> ObjectUpdateResponse:
        pass

    async def delete_object(self, data: dict) -> ObjectDeleteResponse:
        pass