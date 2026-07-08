from typing import AsyncIterable
from sqlalchemy.ext.asyncio import AsyncSession
from dishka import Provider, Scope, provide

from backend.src.v1.auth.domain.interfaces import IRoleRepo, IUserRepo
from backend.src.v1.auth.infrastructure.role_repo import PgRoleRepo
from backend.src.v1.auth.infrastructure.user_repo import PgUserRepo
from backend.src.v1.data.domain.interfaces import IActRepo, ICompanyRepo, IContractRepo, IObjectRepo, IRoadmapRepo, ITaskRepo, IWorkRepo
from backend.src.v1.data.infrastructure.acts_repo import PgActRepo
from backend.src.v1.data.infrastructure.company_repo import PgCompanyRepo
from backend.src.v1.data.infrastructure.contract_repo import PgContractRepo
from backend.src.v1.data.infrastructure.objects_repo import PgObjectRepo
from backend.src.v1.data.infrastructure.roadmap_repo import PgRoadmapRepo
from backend.src.v1.data.infrastructure.tasks_repo import PgTaskRepo
from backend.src.v1.data.infrastructure.works_repo import PgWorkRepo
from backend.src.v1.filesystem.domain.interfaces import IFileRepo
from backend.src.v1.filesystem.infrastructure.file_repo import PgFileRepo

class RepoProvider(Provider):
    @provide(scope = Scope.REQUEST)
    async def user_repo(self, session: AsyncSession) -> AsyncIterable[IUserRepo]:
        yield PgUserRepo(session)

    @provide(scope = Scope.REQUEST)
    async def role_repo(self, session: AsyncSession) -> AsyncIterable[IRoleRepo]:
        yield PgRoleRepo(session)

    @provide(scope=Scope.REQUEST)
    async def file_repo(self, session: AsyncSession) -> AsyncIterable[IFileRepo]:
        yield PgFileRepo(session)

    @provide(scope=Scope.REQUEST)
    async def task_repo(self, session: AsyncSession) -> AsyncIterable[ITaskRepo]:
        yield PgTaskRepo(session)

    @provide(scope=Scope.REQUEST)
    async def object_repo(self, session: AsyncSession) -> AsyncIterable[IObjectRepo]:
        yield PgObjectRepo(session)
    
    @provide(scope=Scope.REQUEST)
    async def roadmap_repo(self, session: AsyncSession) -> AsyncIterable[IRoadmapRepo]:
        yield PgRoadmapRepo(session)

    @provide(scope=Scope.REQUEST)
    async def act_repo(self, session: AsyncSession) -> AsyncIterable[IActRepo]:
        yield PgActRepo(session)

    @provide(scope=Scope.REQUEST)
    async def work_repo(self, session: AsyncSession) -> AsyncIterable[IWorkRepo]:
        yield PgWorkRepo(session)

    @provide(scope=Scope.REQUEST)
    async def company_repo(self, session: AsyncSession) -> AsyncIterable[ICompanyRepo]:
        yield PgCompanyRepo(session)

    @provide(scope=Scope.REQUEST)
    async def contract_repo(self, session: AsyncSession) -> AsyncIterable[IContractRepo]:
        yield PgContractRepo(session)