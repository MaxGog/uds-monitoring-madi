

from typing import AsyncIterable
from sqlalchemy.ext.asyncio import AsyncSession
from dishka import Provider, Scope, provide

from backend.src.v1.auth.domain.interfaces import IUserRepository
from backend.src.v1.auth.infrastructure.user_repo import PGUserRepository

class RepoProvider(Provider):
    @provide(scope = Scope.REQUEST)
    async def user_repo(self, session: AsyncSession) -> AsyncIterable[IUserRepository]:
        yield PGUserRepository(session)