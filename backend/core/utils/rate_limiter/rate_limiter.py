from datetime import time
import random

from fastapi import HTTPException, Request, status
from redis import Redis


class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def is_limited(
            self,
            ip_address: str,
            endpoint: str,
            max_requests: int,
            time_window_seconds: int,
    ) -> bool:
        key = f"rate_limiter:{endpoint}:{ip_address}"

        current_ms = time() * 1000
        window_start_ms = current_ms - time_window_seconds * 1000

        current_request = f"{current_ms}-{random.randint(0, 100_000)}"
        async with self.redis.pipeline() as pipe:
            await pipe.zremrangebyscore(key, 0, window_start_ms)

            await pipe.zcard(key)

            await pipe.zadd(key, mapping = {current_request: current_ms})

            await pipe.expire(key, time_window_seconds)

            result = await pipe.execute()
        _, current_count, _, _ = result
        return current_count > max_requests

def rate_limiter_factory(
        endpoint: str,
        max_requests: int,
        window_seconds: int,
):
    async def dependency(
            request: Request,
            rate_limiter: RateLimiter,
    ):
        ip_address = request.client.host

        limited = await rate_limiter.is_limited(
            ip_address=ip_address,
            endpoint=endpoint,
            max_requests=max_requests,
            time_window_seconds=window_seconds,
        )

        if limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                )
    return dependency