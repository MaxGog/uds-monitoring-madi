from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IWorkRepo, IWorkUsecases


@dataclass
class WorkUsecases(IWorkUsecases):
    uow: IUnitOfWork
    work_repo: IWorkRepo
    user_repo: IUserRepo