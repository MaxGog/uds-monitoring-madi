from dishka import Provider, Scope, provide
import redis

from backend.core.utils.hasher.password_hasher import BCryptPasswordHash


class AuthProvider(Provider):
    @provide(scope=Scope.APP)
    def hasher(self) -> IPasswordHasher:
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