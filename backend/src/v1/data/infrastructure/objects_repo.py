from typing import List, Optional

from sqlalchemy import func, select

from backend.core.db.postgres.data_orms.act_orm import WorkAct
from backend.core.db.postgres.data_orms.object_orm import Object
from backend.src.v1.data.domain.interfaces import IObjectRepo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

class PgObjectRepo(IObjectRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session


    async def get_by_id(self, object_id: int) -> Optional[Object]:
        return await self.session.get(Object, object_id)

    async def get_by_id_with_relations(self, object_id: int) -> Optional[Object]:
        stmt = (
            select(Object)
            .where(Object.id == object_id)
            .options(
                joinedload(Object.supervisor),
                joinedload(Object.contractor)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Object]:
        stmt = (
            select(Object)
            .options(
                joinedload(Object.supervisor),
                joinedload(Object.contractor)
            )
            .order_by(Object.id.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_total_completed_cost(self, object_id: int) -> float:
        stmt = (
            select(func.coalesce(func.sum(WorkAct.total_amount), 0.0))
            .where(WorkAct.object_id == object_id)
        )
        result = await self.session.execute(stmt)
        return float(result.scalar_one())

    async def add(self, obj: Object) -> None:
        self.session.add(obj)

    async def delete(self, obj: Object) -> None:
        await self.session.delete(obj)