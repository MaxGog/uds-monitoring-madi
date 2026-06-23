from pydantic_settings import BaseSettings

from backend.config.auth_config import AuthJWT
from backend.config.filesystem_config import MinIOSettings
from backend.core.db.postgres.postgres_conn import DbSettings
from backend.core.db.redis.redis_conn import RedisSettings


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()
    redis: RedisSettings = RedisSettings()
    minio: MinIOSettings = MinIOSettings()


settings = Settings()