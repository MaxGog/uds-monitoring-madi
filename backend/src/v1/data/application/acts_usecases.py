from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IActRepo, IActUsecases


@dataclass
class ActUsecases(IActUsecases):
    uow: IUnitOfWork
    act_repo: IActRepo
    user_repo: IUserRepo # Для проверки прав доступа просто