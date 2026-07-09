from typing import List, Optional

from sqlalchemy import select

from backend.core.db.postgres.data_orms.company_orm import Company
from backend.src.v1.data.domain.interfaces import ICompanyRepo
from sqlalchemy.ext.asyncio import AsyncSession

class PgCompanyRepo(ICompanyRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_by_id(self, company_id: int) -> Optional[Company]:
        return await self.session.get(Company, company_id)

    async def get_by_inn(self, inn: str) -> Optional[Company]:
        stmt = select(Company).where(Company.inn == inn)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Company]:
        stmt = select(Company).order_by(Company.name.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, company: Company) -> None:
        self.session.add(company)

    async def delete(self, company: Company) -> None:
        await self.session.delete(company)