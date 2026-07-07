from dataclasses import dataclass

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.role_orm import RoleName
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import ICompanyRepo, ICompanyUsecases
from backend.src.v1.data.presentation.dtos.company_dto import CompanyCreateResponse, CompanyDeleteResponse, CompanyResponse, CompanyUpdateResponse, CompaniesResponse


@dataclass
class CompanyUsecases(ICompanyUsecases):
    uow: IUnitOfWork
    company_repo: ICompanyRepo
    user_repo: IUserRepo

    async def get_companies(self, user_id: str,) -> CompanyResponse:
        role = await self.user_repo.get_role(user_id)

        if role not in (RoleName.VIEWER, RoleName.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        # Выполнить проверку прав доступа для кастомной роли

        return await self.company_repo.get_companies()

    async def get_company(self, user_id: str, data: dict) -> CompanysResponse:
        role = await self.user_repo.get_role(user_id)

        if role not in (RoleName.VIEWER, RoleName.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        # Выполнить проверку прав доступа для кастомной роли

        return await self.company_repo.get_company(data['company_id'])

    async def create_company(self, user_id: str, data: dict) -> CompanyCreateResponse:
        role = await self.user_repo.get_role(user_id)

        if role is not RoleName.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        return await self.company_repo.create_company()

    async def update_company(self, user_id: str, data: dict) -> CompanyUpdateResponse:
        role = await self.user_repo.get_role(user_id)

        if role is not RoleName.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        return await self.company_repo.update_company()

    async def delete_company(self, user_id: str, data: dict) -> CompanyDeleteResponse:
        role = await self.user_repo.get_role(user_id)

        if role is not RoleName.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        return await self.company_repo.delete_company()