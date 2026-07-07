from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IRoadmapRepo, IRoadmapUsecases
from backend.src.v1.data.presentation.dtos.roadmap_dto import RoadmapCreateResponse, RoadmapDeleteResponse, RoadmapResponse, RoadmapUpdateResponse, RoadmapsResponse


@dataclass
class RoadmapUsecases(IRoadmapUsecases):
    uow: IUnitOfWork
    roadmap_repo: IRoadmapRepo
    user_repo: IUserRepo

    async def get_roadmaps(self) -> RoadmapResponse:
        pass

    async def get_roadmap(self, data: dict) -> RoadmapsResponse:
        pass

    async def create_roadmap(self, data: dict) -> RoadmapCreateResponse:
        pass

    async def update_roadmap(self, data: dict) -> RoadmapUpdateResponse:
        pass

    async def delete_roadmap(self, data: dict) -> RoadmapDeleteResponse:
        pass