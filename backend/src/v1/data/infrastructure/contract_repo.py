from backend.src.v1.data.domain.interfaces import IContractRepo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.data.presentation.dtos.contract_dto import ContractCreateResponse, ContractDeleteResponse, ContractResponse, ContractUpdateResponse, ContractsResponse

class PgContractRepo(IContractRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_contracts(self) -> ContractsResponse:
        pass

    async def get_contract(self, contract_id: int) -> ContractResponse:
        pass

    async def create_contract(self) -> ContractCreateResponse:
        pass

    async def update_contract(self) -> ContractUpdateResponse:
        pass

    async def delete_contract(self) -> ContractDeleteResponse:
        pass