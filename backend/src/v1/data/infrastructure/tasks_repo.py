from backend.src.v1.data.domain.interfaces import ITaskRepo
from sqlalchemy.ext.asyncio import AsyncSession

class PgTaskRepo(ITaskRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session