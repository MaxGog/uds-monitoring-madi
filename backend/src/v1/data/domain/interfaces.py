from abc import abstractmethod
from typing import List, Optional, Protocol

from backend.core.db.postgres.data_orms.company_orm import Company
from backend.core.db.postgres.data_orms.object_orm import Object
from backend.core.db.postgres.data_orms.task_orm import Task
from backend.core.db.postgres.data_orms.work_orm import Work

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
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[Object]: pass
    
    @abstractmethod
    async def get_by_id_with_relations(self, item_id: int) -> Optional[Object]: pass
    
    @abstractmethod
    async def get_all(self) -> List[Object]: pass
    
    @abstractmethod
    async def get_total_completed_cost(self, item_id: int) -> float: pass
    
    @abstractmethod
    async def add(self, obj: Object) -> None: pass
    
    @abstractmethod
    async def delete(self, obj: Object) -> None: pass

class IWorkRepo(Protocol):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[Work]: pass
    
    @abstractmethod
    async def get_by_id_with_relations(self, item_id: int) -> Optional[Work]: pass
    
    @abstractmethod
    async def get_all(self) -> List[Work]: pass
    
    @abstractmethod
    async def add(self, work: Work) -> None: pass
    
    @abstractmethod
    async def delete(self, work: Work) -> None: pass

class IActRepo(Protocol):
    ...

class IRoadmapRepo(Protocol):
    ...

class ICompanyRepo(Protocol):
    @abstractmethod
    async def get_by_id(self, company_id: int) -> Optional[Company]: pass
    
    @abstractmethod
    async def get_by_inn(self, inn: str) -> Optional[Company]: pass
    
    @abstractmethod
    async def get_all(self) -> List[Company]: pass
    
    @abstractmethod
    async def add(self, company: Company) -> None: pass
    
    @abstractmethod
    async def delete(self, company: Company) -> None: pass

class IContractRepo(Protocol):
    ...