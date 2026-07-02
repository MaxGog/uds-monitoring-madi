from backend.src.v1.data.domain.interfaces import IObjectRepo
from sqlalchemy.ext.asyncio import AsyncSession

class PgObjectRepo(IObjectRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session