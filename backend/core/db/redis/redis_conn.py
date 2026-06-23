from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    REDIS_HOST: str = Field(alias="REDIS_HOST")
    REDIS_PORT: int = Field(alias="REDIS_PORT")
    REDIS_PASS: str = Field(alias="REDIS_PASS")
    

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra = "ignore"
    )
    @property
    def REDIS_URL(self) -> str:
        # Формат: redis://[:password]@host:port/db
        return f"redis://default:{self.REDIS_PASS}@{self.REDIS_HOST}:{self.REDIS_PORT}"