from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import ITaskRepo, ITaskUsecases


@dataclass
class TaskUsecases(ITaskUsecases):
    uow: IUnitOfWork
    task_repo: ITaskRepo
    user_repo: IUserRepo