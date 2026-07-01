

from typing import AsyncIterable
from sqlalchemy.ext.asyncio import AsyncSession
from dishka import Provider, Scope, provide

from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.auth.infrastructure.user_repo import PGUserRepo
from backend.src.v1.filesystem.domain.interfaces import IFileRepo
from backend.src.v1.filesystem.infrastructure.file_repo import PgFileRepo

class RepoProvider(Provider):
    @provide(scope = Scope.REQUEST)
    async def user_repo(self, session: AsyncSession) -> AsyncIterable[IUserRepo]:
        yield PGUserRepo(session)

    @provide(scope=Scope.REQUEST)
    async def file_repo(self, session: AsyncSession) -> AsyncIterable[IFileRepo]:
        yield PgFileRepo(session)