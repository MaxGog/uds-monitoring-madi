from dataclasses import dataclass

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo, IUserUsecases
from backend.src.v1.auth.presentation.dto.user_dto import UserResponseDTO


@dataclass
class UserUsecases(IUserUsecases):
    uow: IUnitOfWork
    user_repo: IUserRepo

    async def get_users(self, limit: int = 20, offset: int = 0) -> UserResponseDTO:
        return await self.user_repo.get_all(limit = limit, offset = offset)

