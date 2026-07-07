from backend.src.v1.data.domain.interfaces import ICompanyRepo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.data.presentation.dtos.company_dto import CompanyCreateResponse, CompanyDeleteResponse, CompanyResponse, CompanyUpdateResponse, CompaniesResponse

class PgCompanyRepo(ICompanyRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_companies(self) -> CompaniesResponse:
        pass

    async def get_company(self, company_id: int) -> CompanyResponse:
        pass

    async def create_company(self) -> CompanyCreateResponse:
        pass

    async def update_company(self) -> CompanyUpdateResponse:
        pass

    async def delete_company(self) -> CompanyDeleteResponse:
        pass