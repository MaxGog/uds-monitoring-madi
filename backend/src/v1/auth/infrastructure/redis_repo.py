import redis

from backend.src.v1.auth.domain.interfaces import ITokenProvider, ITokenStorage


class RedisTokenStorage(ITokenStorage):
    def __init__(self, client: redis.Redis, token_provider: ITokenProvider):
        self.redis = client
        self.code_ttl = 300
        self.token_provider = token_provider
        self.max_sessions = 5