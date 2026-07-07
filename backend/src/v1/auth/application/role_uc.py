from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IRoleRepo, IRoleUsecases, IUserRepo


@dataclass
class RoleUsecases(IRoleUsecases):
    uow: IUnitOfWork
    user_repo: IUserRepo
    role_repo: IRoleRepo
