from typing import List, Optional

from sqlalchemy import select

from backend.core.db.postgres.data_orms.task_orm import Task
from backend.src.v1.data.domain.interfaces import ITaskRepo

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

class PgTaskRepo(ITaskRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_by_id(self, item_id: int) -> Optional[Task]:
        return await self.session.get(Task, item_id)

    async def get_by_id_with_relations(self, task_id: int) -> Optional[Task]:
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .options(
                joinedload(Task.author),
                selectinload(Task.performers)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Task]:
        stmt = (
            select(Task)
            .options(
                joinedload(Task.author),
                selectinload(Task.performers)
            )
            .order_by(Task.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, task: Task) -> None:
        self.session.add(task)

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)