from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IActRepo, IActUsecases
from backend.src.v1.data.presentation.dtos.act_dto import ActCreateResponse, ActDeleteResponse, ActResponse, ActUpdateResponse, ActsResponse


@dataclass
class ActUsecases(IActUsecases):
    uow: IUnitOfWork
    act_repo: IActRepo
    user_repo: IUserRepo # Для проверки прав доступа просто

    async def get_acts(self) -> ActResponse:
        pass

    async def get_act(self, data: dict) -> ActsResponse:
        pass

    async def create_act(self, data: dict) -> ActCreateResponse:
        pass

    async def update_act(self, data: dict) -> ActUpdateResponse:
        pass

    async def delete_act(self, data: dict) -> ActDeleteResponse:
        pass