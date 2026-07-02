from backend.src.v1.data.domain.interfaces import IWorkRepo
from sqlalchemy.ext.asyncio import AsyncSession

class PgWorkRepo(IWorkRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session