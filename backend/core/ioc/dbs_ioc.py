from typing import AsyncGenerator, AsyncIterable
from minio import Minio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from dishka import Provider, Scope, provide
import redis.asyncio as redis

from backend.config.config import settings, Settings
from backend.core.db.postgres.unit_of_work import IUnitOfWork, SQLAlchemyUnitOfWork
from backend.core.db.postgres.postgres_conn import db_engine
from backend.core.db.redis.redis_conn import redis_client


class DbProvider(Provider):
    @provide(scope=Scope.APP)
    def config(self) -> Settings:
        return settings

    @provide(scope=Scope.APP)
    def get_redis(self) -> redis.Redis:
        return redis_client

    @provide(scope=Scope.APP)
    async def get_engine(self) -> AsyncEngine:
        return db_engine
    
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