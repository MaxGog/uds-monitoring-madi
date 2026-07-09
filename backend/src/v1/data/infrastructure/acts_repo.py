from typing import List, Optional

from sqlalchemy import select

from backend.core.db.postgres.data_orms.act_orm import WorkAct
from backend.src.v1.data.domain.interfaces import IActRepo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

class PgActRepo(IActRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
  
    async def get_by_id(self, act_id: int) -> Optional[WorkAct]:
        return await self.session.get(WorkAct, act_id)

    async def get_by_id_with_relations(self, act_id: int) -> Optional[WorkAct]:
        stmt = (
            select(WorkAct)
            .where(WorkAct.id == act_id)
            .options(
                joinedload(WorkAct.object),
                joinedload(WorkAct.work),
                joinedload(WorkAct.contract),
                selectinload(WorkAct.items) # Загружаем позиции акта
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[WorkAct]:
        stmt = (
            select(WorkAct)
            .options(selectinload(WorkAct.items))
            .order_by(WorkAct.date_signed.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, act: WorkAct) -> None:
        self.session.add(act)

    async def delete(self, act: WorkAct) -> None:
        await self.session.delete(act)