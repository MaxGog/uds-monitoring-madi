import logging

from dishka import Provider, Scope, provide
import redis.asyncio as redis

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.core.utils.hasher.password_hasher import BCryptPasswordHash
from backend.core.utils.jwt_service.jwt_service import TokenAuth, TokenProvider
from backend.src.v1.auth.application.usecases import AuthUsecases
from backend.src.v1.auth.domain.interfaces import IAuthUsecases, IPasswordHasher, ITokenAuth, ITokenProvider, ITokenStorage, IUserRepository
from backend.src.v1.auth.infrastructure.redis_repo import RedisTokenStorage

logger = logging.getLogger("auth_ioc")

class AuthProvider(Provider):
    @provide(scope=Scope.APP)
    def hasher(self) -> IPasswordHasher:
        logger.debug("Injecting BCrypt")
        return BCryptPasswordHash()

    @provide(scope=Scope.SESSION)
    def token_provider(self) -> ITokenProvider:
        return TokenProvider()
    
    @provide(scope=Scope.REQUEST)
    def token_auth(self, provider: ITokenProvider, storage: ITokenStorage) -> ITokenAuth:
        return TokenAuth(token_provider=provider, token_storage=storage)
    
    @provide(scope=Scope.REQUEST)
    def redis_storage(self, r: redis.Redis, token_provider: ITokenProvider) -> ITokenStorage:
        return RedisTokenStorage(r, token_provider)
    
    @provide(scope = Scope.REQUEST)
    def get_auth_uc(self, uow: IUnitOfWork, token_storage: ITokenStorage, token_service: ITokenAuth, token_provider: ITokenProvider, hasher: IPasswordHasher) -> IAuthUsecases:
        return AuthUsecases(uow=uow, token_repo=token_storage, token_service=token_service, token_provider=token_provider, hasher=hasher)