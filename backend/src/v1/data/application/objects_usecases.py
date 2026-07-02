from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IObjectRepo, IObjectUsecases


@dataclass
class ObjectUsecases(IObjectUsecases):
    uow: IUnitOfWork
    object_repo: IObjectRepo
    user_repo: IUserRepo