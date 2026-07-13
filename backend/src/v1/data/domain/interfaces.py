from abc import abstractmethod
from typing import List, Optional, Protocol

from backend.core.db.postgres.data_orms.act_orm import Act
from backend.core.db.postgres.data_orms.company_orm import Company
from backend.core.db.postgres.data_orms.contract_orm import Contract
from backend.core.db.postgres.data_orms.object_orm import Object
from backend.core.db.postgres.data_orms.task_orm import Task
from backend.core.db.postgres.data_orms.work_orm import Work
from backend.src.v1.data.presentation.dtos.act_dto import ActCreateRequest, ActResponse, ActUpdateRequest
from backend.src.v1.data.presentation.dtos.company_dto import CompanyCreateRequest, CompanyResponse, CompanyUpdateRequest
from backend.src.v1.data.presentation.dtos.contract_dto import ContractCreateRequest, ContractResponse, ContractUpdateRequest
from backend.src.v1.data.presentation.dtos.object_dto import ObjectCreateRequest, ObjectResponse, ObjectUpdateRequest
from backend.src.v1.data.presentation.dtos.task_dto import TaskCreateRequest, TaskResponse, TaskUpdateRequest
from backend.src.v1.data.presentation.dtos.work_dto import WorkCreateRequest, WorkResponse, WorkUpdateRequest

class ITaskUsecases(Protocol):
    @abstractmethod
    async def get_tasks(self) -> List[TaskResponse]: pass

    @abstractmethod
    async def get_task_by_id(self, item_id: int) -> TaskResponse: pass

    @abstractmethod
    async def create_task(self, author_id: str, data: TaskCreateRequest) -> TaskResponse: pass

    @abstractmethod
    async def update_task(self, item_id: int, data: TaskUpdateRequest) -> TaskResponse: pass

    @abstractmethod
    async def delete_task(self, item_id: int) -> None: pass

class IObjectUsecases(Protocol):
    @abstractmethod
    async def get_objects(self) -> List[ObjectResponse]: pass

    @abstractmethod
    async def get_object_by_id(self, item_id: int) -> ObjectResponse: pass

    @abstractmethod
    async def create_object(self, data: ObjectCreateRequest) -> ObjectResponse: pass

    @abstractmethod
    async def update_object(self, item_id: int, data: ObjectUpdateRequest) -> ObjectResponse: pass

    @abstractmethod
    async def delete_object(self, item_id: int) -> None: pass

class IWorkUsecases(Protocol):
    @abstractmethod
    async def get_work_by_id(self, item_id: int) -> WorkResponse: pass

    @abstractmethod
    async def get_all_works(self) -> List[WorkResponse]: pass

    @abstractmethod
    async def create_work(self, data: WorkCreateRequest) -> WorkResponse: pass

    @abstractmethod
    async def update_work(self, item_id: int, data: WorkUpdateRequest) -> WorkResponse: pass

    @abstractmethod
    async def delete_work(self, item_id: int) -> None: pass

class IActUsecases(Protocol):
    @abstractmethod
    async def get_act_by_id(self, item_id: int) -> ActResponse: pass

    @abstractmethod
    async def get_all_acts(self) -> List[ActResponse]: pass

    @abstractmethod
    async def create_act(self, data: ActCreateRequest) -> ActResponse: pass

    @abstractmethod
    async def update_act(self, item_id: int, data: ActUpdateRequest) -> ActResponse: pass

    @abstractmethod
    async def delete_act(self, item_id: int) -> None: pass

class IRoadmapUsecases(Protocol):
    ...

class ICompanyUsecases(Protocol):
    @abstractmethod
    async def create_company(self, data: CompanyCreateRequest) -> CompanyResponse: pass

    @abstractmethod
    async def get_company_by_id(self, item_id: int) -> CompanyResponse: pass

    @abstractmethod
    async def get_all_companies(self) -> List[CompanyResponse]: pass

    @abstractmethod
    async def update_company(self, item_id: int, data: CompanyUpdateRequest) -> CompanyResponse: pass

    @abstractmethod
    async def delete_company(self, item_id: int) -> None: pass

class IContractUsecases(Protocol):
    @abstractmethod
    async def get_contract_by_id(self, item_id: int) -> ContractResponse: pass

    @abstractmethod
    async def get_all_contracts(self) -> List[ContractResponse]: pass

    @abstractmethod
    async def create_contract(self, data: ContractCreateRequest) -> ContractResponse: pass

    @abstractmethod
    async def update_contract(self, item_id: int, data: ContractUpdateRequest) -> ContractResponse: pass

    @abstractmethod
    async def delete_contract(self, item_id: int) -> None: pass


class ITaskRepo(Protocol):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[Task]: ...

    @abstractmethod
    async def get_by_id_with_relations(self, item_id: int) -> Optional[Task]: ...

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
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[Act]: pass
    
    @abstractmethod
    async def get_by_id_with_relations(self, item_id: int) -> Optional[Act]: pass
    
    @abstractmethod
    async def get_all(self) -> List[Act]: pass
    
    @abstractmethod
    async def add(self, act: Act) -> None: pass
    
    @abstractmethod
    async def delete(self, act: Act) -> None: pass

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
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[Contract]: pass
    
    @abstractmethod
    async def get_by_id_with_relations(self, item_id: int) -> Optional[Contract]: pass
    
    @abstractmethod
    async def get_all(self) -> List[Contract]: pass
    
    @abstractmethod
    async def add(self, contract: Contract) -> None: pass
    
    @abstractmethod
    async def delete(self, contract: Contract) -> None: pass