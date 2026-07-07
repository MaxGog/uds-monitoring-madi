from backend.src.v1.data.domain.interfaces import IActRepo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.data.presentation.dtos.act_dto import ActCreateResponse, ActDeleteResponse, ActResponse, ActUpdateResponse, ActsResponse

class PgActRepo(IActRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
  
    async def get_acts(self) -> ActsResponse:
        pass

    async def get_act(self, act_id: int) -> ActResponse:
        pass

    async def create_act(self) -> ActCreateResponse:
        pass

    async def update_act(self) -> ActUpdateResponse:
        pass

    async def delete_act(self) -> ActDeleteResponse:
        pass