import logging
from redis.asyncio import Redis as redis
from redis.exceptions import RedisError

from backend.config.config import settings

logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.redis.REDIS_URL, decode_responses=True)

async def check_redis_connection(redis_client: redis) -> bool:
    """
    Проверяет асинхронное соединение с Redis с помощью команды PING.
    """
    try:
        response = await redis_client.ping()
        if response:
            logger.info("Successfully connected to Redis.")
            return True
        logger.error("Redis ping returned unexpected response.")
        return False
    except RedisError as e:
        logger.error(f"Redis connection health check failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during Redis health check: {e}")
        return False