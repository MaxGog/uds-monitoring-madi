from backend.src.v1.data.domain.interfaces import IRoadmapRepo
from sqlalchemy.ext.asyncio import AsyncSession

class PgRoadmapRepo(IRoadmapRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session