from datetime import datetime
import json

from backend.src.v1.auth.domain.interfaces import ITokenProvider, ITokenStorage
import redis.asyncio as redis

from backend.src.v1.auth.domain.models import CodeData

class RedisTokenStorage(ITokenStorage):
    def __init__(self, client: redis.Redis, token_provider: ITokenProvider):
        self.redis = client
        self.code_ttl = 300
        self.token_provider = token_provider
        self.max_sessions = 5

    async def get_and_delete_code(self, code: str) -> CodeData | None:
        '''
        PKCE flow
        Нужен для работы с challenge code.
        '''
        key = f"auth_code:{code}"
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.get(key)
            pipe.delete(key)
            result, _ = await pipe.execute()
        if not result:
            return None
        try:
            return CodeData.from_json(result)
        except (json.JSONDecodeError, TypeError):
            return None

    async def save_code(self, code: str, user_id: int, challenge: str, code_ttl: int = 600):
        data = CodeData(user_id=user_id, challenge=challenge)
        key = f"auth_code:{code}"
        await self.redis.setex(key, code_ttl, data.to_json())


    def _key(self, user_id: int) -> str:
        # Просто реализует единообразие по ключу для сессий
        return f"user_sessions:{user_id}"

    async def add_session(self, user_id: int, access_jti: str, refresh_jti: str, expire_seconds: int):
        # Создаёт новую сессию, храня пару a_jti:r_jti
        key = self._key(user_id)
        val = f"{access_jti}:{refresh_jti}"
        
        async with self.redis.pipeline(transaction=True) as pipe:
            await pipe.zadd(key, {val: int(datetime.now().timestamp())})
            await pipe.zremrangebyrank(key, 0, -(self.max_sessions + 1))
            await pipe.expire(key, expire_seconds)
            await pipe.execute()

    async def is_token_valid(self, user_id: int, a_jti: str) -> bool:
        # имеется ли активный access токен с таким jti
        sessions = await self.redis.zrange(self._key(user_id), 0, -1)
        return any(s.startswith(f"{a_jti}:") for s in sessions)

    async def is_session_valid(self, user_id: int, a_jti: str, r_jti: str) -> bool:
        sessions = await self.redis.zrange(self._key(user_id), 0, -1)
        # Ищем, есть ли активная сессия с таким access_jti и refresh_jti
        return any(s.startswith(f"{a_jti}:{r_jti}") for s in sessions)


    async def rotate_session(self, user_id: int, old_value: str, new_value: str, expire_seconds: int):
        # Если посылать много запросов, то может один на миллион раз добавить новую пару токенов,
        # вместо замены старой (при перезагрузке FastAPI, например)
        key = self._key(user_id)
        async with self.redis.pipeline(transaction=True) as pipe:
            await pipe.zrem(key, old_value)
            await pipe.zadd(key, {new_value: int(datetime.now().timestamp())})
            await pipe.zremrangebyrank(key, 0, -(self.max_sessions + 1))
            await pipe.expire(key, expire_seconds)
            await pipe.execute()

    async def remove_session(self, user_id: int, a_jti: str, r_jti: str):
        val = f"{a_jti}:{r_jti}"
        await self.redis.zrem(self._key(user_id), val)

    async def remove_all_sessions(self, user_id: int):
        await self.redis.delete(self._key(user_id))

    @property
    async def client(self):
        return self.redis