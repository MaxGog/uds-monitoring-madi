from dataclasses import dataclass

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.role_orm import RoleName
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IContractRepo, IContractUsecases
from backend.src.v1.data.presentation.dtos.contract_dto import ContractCreateResponse, ContractDeleteResponse, ContractResponse, ContractUpdateResponse, ContractsResponse


@dataclass
class ContractUsecases(IContractUsecases):
    uow: IUnitOfWork
    contract_repo: IContractRepo
    user_repo: IUserRepo

    async def get_contracts(self, user_id: str,) -> ContractResponse:
        role = await self.user_repo.get_role(user_id)

        if role not in (RoleName.VIEWER, RoleName.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        # Выполнить проверку прав доступа для кастомной роли

        return await self.contract_repo.get_contracts()

    async def get_contract(self, user_id: str, data: dict) -> ContractsResponse:
        role = await self.user_repo.get_role(user_id)

        if role not in (RoleName.VIEWER, RoleName.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        # Выполнить проверку прав доступа для кастомной роли

        return await self.contract_repo.get_contract(data['contract_id'])

    async def create_contract(self, user_id: str, data: dict) -> ContractCreateResponse:
        role = await self.user_repo.get_role(user_id)

        if role is not RoleName.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        return await self.contract_repo.create_contract()

    async def update_contract(self, user_id: str, data: dict) -> ContractUpdateResponse:
        role = await self.user_repo.get_role(user_id)

        if role is not RoleName.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        return await self.contract_repo.update_contract()

    async def delete_contract(self, user_id: str, data: dict) -> ContractDeleteResponse:
        role = await self.user_repo.get_role(user_id)

        if role is not RoleName.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        return await self.contract_repo.delete_contract()