from backend.src.v1.data.domain.interfaces import IRoadmapRepo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.data.presentation.dtos.roadmap_dto import RoadmapCreateResponse, RoadmapDeleteResponse, RoadmapResponse, RoadmapUpdateResponse, RoadmapsResponse

class PgRoadmapRepo(IRoadmapRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_roadmaps(self) -> RoadmapsResponse:
        pass

    async def get_roadmap(self, roadmap_id: int) -> RoadmapResponse:
        pass

    async def create_roadmap(self) -> RoadmapCreateResponse:
        pass

    async def update_roadmap(self) -> RoadmapUpdateResponse:
        pass

    async def delete_roadmap(self) -> RoadmapDeleteResponse:
        pass