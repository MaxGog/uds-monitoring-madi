from abc import abstractmethod
from typing import List, Optional, Protocol

from backend.core.db.postgres.data_orms.task_orm import Task

class ITaskUsecases(Protocol):
    ...

class IObjectUsecases(Protocol):
    ...

class IWorkUsecases(Protocol):
    ...

class IActUsecases(Protocol):
    ...

class IRoadmapUsecases(Protocol):
    ...

class ICompanyUsecases(Protocol):
    ...

class IContractUsecases(Protocol):
    ...



class ITaskRepo(Protocol):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[Task]: ...

    @abstractmethod
    async def get_by_id_with_users(self, item_id: int) -> Optional[Task]: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Task]: ...

    @abstractmethod
    async def get_all(self) -> List[Task]: ...

    @abstractmethod
    async def add(self, task: Task) -> None: ...

    @abstractmethod
    async def delete(self, task: Task) -> None: ...

class IObjectRepo(Protocol):
    ...

class IWorkRepo(Protocol):
    ...

class IActRepo(Protocol):
    ...

class IRoadmapRepo(Protocol):
    ...

class ICompanyRepo(Protocol):
    ...

class IContractRepo(Protocol):
    ...