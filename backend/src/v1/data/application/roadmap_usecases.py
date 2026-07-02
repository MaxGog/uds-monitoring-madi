from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IRoadmapRepo, IRoadmapUsecases


@dataclass
class RoadmapUsecases(IRoadmapUsecases):
    uow: IUnitOfWork
    roadmap_repo: IRoadmapRepo
    user_repo: IUserRepo