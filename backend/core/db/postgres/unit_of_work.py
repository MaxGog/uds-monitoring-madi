from abc import abstractmethod
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.auth.domain.interfaces import IPermissionRepo, IRoleRepo, IUserRepo
from backend.src.v1.auth.infrastructure.permission_repo import PgPermissionRepo
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


# Автоматический хелпер для работы с асинхронными транзакциями через контекстный менеджер. Сразу через интерфейс.

class IUnitOfWork(Protocol):
    session: AsyncSession
    user_repo: IUserRepo
    file_repo: IFileRepo
    permission_repo: IPermissionRepo
    role_repo: IRoleRepo
    act_repo: IActRepo
    company_repo: ICompanyRepo
    contract_repo: IContractRepo
    object_repo: IObjectRepo
    roadmap_repo: IRoadmapRepo
    task_repo: ITaskRepo
    work_repo: IWorkRepo


    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    async def __aexit__(self, *args): ...

class SQLAlchemyUnitOfWork(IUnitOfWork):
    '''
    Внутрь паттерна передаются репозитории. Другие варианты были испробованы, но они оказались несильно лучше.
    '''
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = PgUserRepo(session)
        self.file_repo = PgFileRepo(session)
        self.permission_repo = PgPermissionRepo(session)
        self.role_repo = PgRoleRepo(session)
        self.act_repo = PgActRepo(session)
        self.company_repo = PgCompanyRepo(session)
        self.contract_repo = PgContractRepo(session)
        self.object_repo = PgObjectRepo(session)
        self.roadmap_repo = PgRoadmapRepo(session)
        self.task_repo = PgTaskRepo(session)
        self.work_repo = PgWorkRepo(session)
        
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # При ошибке автоматически откатывает транзакцию.
            #await self.rollback()
            # Может изредка вызвать циклический rollback
            pass
        else:
            pass


    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.rollback()