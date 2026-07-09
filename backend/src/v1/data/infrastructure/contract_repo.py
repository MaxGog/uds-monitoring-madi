from typing import List, Optional

from sqlalchemy import select

from backend.core.db.postgres.data_orms.contract_orm import Contract
from backend.src.v1.data.domain.interfaces import IContractRepo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

class PgContractRepo(IContractRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_by_id(self, id: int) -> Optional[Contract]:
        return await self.session.get(Contract, id)

    async def get_by_id_with_relations(self, id: int) -> Optional[Contract]:
        stmt = (
            select(Contract)
            .where(Contract.id == id)
            .options(
                joinedload(Contract.object),
                joinedload(Contract.work),
                selectinload(Contract.items)  # Загружаем коллекцию позиций договора
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Contract]:
        stmt = (
            select(Contract)
            .options(selectinload(Contract.items))
            .order_by(Contract.id.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, contract: Contract) -> None:
        self.session.add(contract)

    async def delete(self, contract: Contract) -> None:
        await self.session.delete(contract)