from typing import AsyncGenerator, AsyncIterable
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from dishka import Provider, Scope, provide
import redis

from backend.config.config import settings, Settings
from backend.core.db.postgres.unit_of_work import IUnitOfWork, SQLAlchemyUnitOfWork


class DbProvider(Provider):
    @provide(scope=Scope.APP)
    def config(self) -> Settings:
        return settings

    @provide(scope=Scope.APP)
    async def get_redis(self, cfg: Settings) -> redis.Redis:
        return redis.from_url(cfg.redis.REDIS_URL, decode_responses=True)


    @provide(scope=Scope.APP)
    def engine(self) -> AsyncEngine:
        engine = create_async_engine(
            settings.db.DB_URL,
            echo = settings.db.ECHO,
            echo_pool = settings.db.ECHO_POOL,
            pool_pre_ping = settings.db.POOL_PRE_PING,
            pool_size = settings.db.POOL_SIZE, 
        )
        return engine
    
    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def session(self, session_factory: async_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session
    
    @provide(scope=Scope.REQUEST)
    async def uow(self, session: AsyncSession) -> AsyncIterable[IUnitOfWork]:
        yield SQLAlchemyUnitOfWork(session)