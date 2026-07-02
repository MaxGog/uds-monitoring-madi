from backend.src.v1.data.domain.interfaces import IActRepo
from sqlalchemy.ext.asyncio import AsyncSession

class PgActRepo(IActRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session