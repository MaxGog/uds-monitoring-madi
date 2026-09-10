from typing import List, Optional

from sqlalchemy import select

from backend.core.db.postgres.data_orms.work_orm import Work
from backend.src.v1.data.domain.interfaces import IWorkRepo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

class PgWorkRepo(IWorkRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session


    async def get_by_id(self, work_id: int) -> Optional[Work]:
        return await self.session.get(Work, work_id)

    async def get_by_id_with_relations(self, work_id: int) -> Optional[Work]:
        stmt = (
            select(Work)
            .where(Work.id == work_id)
            .options(
                joinedload(Work.object),
                joinedload(Work.contractor)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Work]:
        stmt = (
            select(Work)
            .options(
                joinedload(Work.object),
                joinedload(Work.contractor)
            )
            .order_by(Work.deadline.asc()) # Сортируем по приближению дедлайна
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, work: Work) -> None:
        self.session.add(work)

    async def delete(self, work: Work) -> None:
        await self.session.delete(work)