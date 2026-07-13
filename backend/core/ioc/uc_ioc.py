


from dishka import Provider, Scope, provide

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.application.role_uc import RoleUsecases
from backend.src.v1.auth.application.user_uc import UserUsecases
from backend.src.v1.auth.domain.interfaces import IPasswordHasher, IRoleRepo, IRoleUsecases, IUserRepo, IUserUsecases
from backend.src.v1.data.application.acts_usecases import ActUsecases
from backend.src.v1.data.application.company_usecases import CompanyUsecases
from backend.src.v1.data.application.contract_usecases import ContractUsecases
from backend.src.v1.data.application.objects_usecases import ObjectUsecases
from backend.src.v1.data.application.roadmap_usecases import RoadmapUsecases
from backend.src.v1.data.application.tasks_usecases import TaskUsecases
from backend.src.v1.data.application.work_usecases import WorkUsecases
from backend.src.v1.data.domain.interfaces import IActRepo, IActUsecases, ICompanyRepo, ICompanyUsecases, IContractRepo, IContractUsecases, IObjectRepo, IObjectUsecases, IRoadmapRepo, IRoadmapUsecases, ITaskRepo, ITaskUsecases, IWorkRepo, IWorkUsecases
from backend.src.v1.filesystem.application.file_uc import FsUsecases
from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFileRepo, IFsUsecases

    # @provide(scope=Scope.REQUEST)
    # async def get_change_uc(self, uow: IUnitOfWork, change_repo: IHangeRepo, user_repo: IUserRepo) -> IHangeUsecases:
    #     return HangeUsecases(self, uow = uow, change_repo=change_repo, user_repo=user_repo)    


class UsecaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_user_uc(self, uow: IUnitOfWork, hasher: IPasswordHasher, user_repo: IUserRepo) -> IUserUsecases:
        return UserUsecases(uow = uow, hasher = hasher, user_repo = user_repo)

    @provide(scope=Scope.REQUEST)
    async def get_role_uc(self, uow: IUnitOfWork,user_repo: IUserRepo, role_repo: IRoleRepo) -> IRoleUsecases:
        return RoleUsecases(uow = uow, user_repo = user_repo, role_repo = role_repo)

    @provide(scope=Scope.REQUEST)
    async def get_fs_uc(self, aws_service: IAwsService, uow: IUnitOfWork, file_repo: IFileRepo, user_repo: IUserRepo) -> IFsUsecases:
        return FsUsecases(aws_service = aws_service, uow = uow, file_repo = file_repo, user_repo = user_repo)

    @provide(scope=Scope.REQUEST)
    async def get_task_uc(self, uow: IUnitOfWork, task_repo: ITaskRepo, user_repo: IUserRepo) -> ITaskUsecases:
        return TaskUsecases(uow = uow, task_repo=task_repo, user_repo=user_repo)
    
    @provide(scope=Scope.REQUEST)
    async def get_object_uc(self, uow: IUnitOfWork, object_repo: IObjectRepo, user_repo: IUserRepo) -> IObjectUsecases:
        return ObjectUsecases(uow = uow, object_repo=object_repo, user_repo=user_repo)
    
    @provide(scope=Scope.REQUEST)
    async def get_act_uc(self, uow: IUnitOfWork, act_repo: IActRepo, user_repo: IUserRepo) -> IActUsecases:
        return ActUsecases(uow = uow, act_repo=act_repo, user_repo=user_repo)    
    
    @provide(scope=Scope.REQUEST)
    async def get_roadmap_uc(self, uow: IUnitOfWork, roadmap_repo: IRoadmapRepo, user_repo: IUserRepo) -> IRoadmapUsecases:
        return RoadmapUsecases(uow = uow, roadmap_repo=roadmap_repo, user_repo=user_repo)
    
    @provide(scope=Scope.REQUEST)
    async def get_work_uc(self, uow: IUnitOfWork, work_repo: IWorkRepo, user_repo: IUserRepo) -> IWorkUsecases:
        return WorkUsecases(uow = uow, work_repo=work_repo, user_repo=user_repo)
    
    @provide(scope=Scope.REQUEST)
    async def get_company_uc(self, uow: IUnitOfWork, company_repo: ICompanyRepo, user_repo: IUserRepo) -> ICompanyUsecases:
        return CompanyUsecases(uow = uow, company_repo = company_repo, user_repo=user_repo)
    
    @provide(scope=Scope.REQUEST)
    async def get_contract_uc(self, uow: IUnitOfWork, contract_repo: IContractRepo, user_repo: IUserRepo) -> IContractUsecases:
        return ContractUsecases(uow = uow, contract_repo = contract_repo, user_repo=user_repo)
    


    