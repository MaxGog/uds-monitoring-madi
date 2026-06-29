import logging

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text
from backend.config.config import settings

logger = logging.getLogger(__name__)

def engine() -> AsyncEngine:
    engine = create_async_engine(
        settings.db.DB_URL,
        echo = settings.db.ECHO,
        echo_pool = settings.db.ECHO_POOL,
        pool_pre_ping = settings.db.POOL_PRE_PING,
        pool_size = settings.db.POOL_SIZE, 
    )

    return engine

async def check_db_connection(engine: AsyncEngine):
    try:
        async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info('Successfully connected to PostgreSQL')
                return True
    except Exception as e:
         logger.error('Error connecting to PostgreSQL: {e}')
         return False
    logger.error('Unknown error connecting to PostgreSQL')
    return False

db_engine = engine()