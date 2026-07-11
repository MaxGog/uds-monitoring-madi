from typing import List, Optional

from sqlalchemy import select

from backend.core.db.postgres.data_orms.act_orm import Act
from backend.src.v1.data.domain.interfaces import IActRepo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

class PgActRepo(IActRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
  
    async def get_by_id(self, act_id: int) -> Optional[Act]:
        return await self.session.get(Act, act_id)

    async def get_by_id_with_relations(self, act_id: int) -> Optional[Act]:
        stmt = (
            select(Act)
            .where(Act.id == act_id)
            .options(
                joinedload(Act.object),
                joinedload(Act.work),
                joinedload(Act.contract),
                selectinload(Act.items) # Загружаем позиции акта
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Act]:
        stmt = (
            select(Act)
            .options(selectinload(Act.items))
            .order_by(Act.date_signed.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, act: Act) -> None:
        self.session.add(act)

    async def delete(self, act: Act) -> None:
        await self.session.delete(act)