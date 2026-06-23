from pathlib import Path
from typing import Any, Dict, Tuple, Type

from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from sqlalchemy import URL
import yaml


BASE_DIR = Path(__file__).parent.parent

YAML_FILE_PATH = BASE_DIR / "config.yml"
class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    """
    Источник настроек, который читает YAML файл и позволяет Pydantic 
    автоматически сопоставлять верхнеуровневые ключи (postgres, redis) 
    с вложенными моделями.
    """
    def get_field_value(self, field_name: str, field_value: Any) -> Tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> Dict[str, Any]:
        if not YAML_FILE_PATH.exists():
            return {}
            
        with open(YAML_FILE_PATH, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            return config_data if config_data else {}

class DbSettings(BaseSettings):
    DB_USER: str = Field(alias="PostgresqlUser")
    DB_PASS: str = Field(alias="PostgresqlPassword")
    DB_NAME: str = Field(alias="PostgresqlDbname")
    DB_DRIVER: str = Field(alias="PgDriver", default="postgresql+asyncpg")
    DB_HOST: str = Field(alias="PostgresqlHost")
    DB_PORT: int = Field(alias="PostgresqlPort")
    SSL_MODE: str = Field(alias="PostgresqlSslmode", default="disable")

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra = "ignore"
    )
    
    @property
    def DB_URL(self) -> str:
        return URL.create(
            drivername=self.DB_DRIVER,
            database=self.DB_NAME,
            host=self.DB_HOST,
            port=self.DB_PORT,
            username=self.DB_USER,
            password=self.DB_PASS,
        ).render_as_string(hide_password=False)
    
    @property
    def ECHO(self) -> bool: return True
    @property
    def ECHO_POOL(self) -> bool: return True
    @property
    def POOL_PRE_PING(self) -> bool: return True
    @property
    def POOL_SIZE(self) -> int: return 10
    
    
    #f"postgresql+asyncpg://my_admin:secret@localhost/app_db"

class RedisSettings(BaseSettings):
    REDIS_ADDR: str = Field(alias="RedisAddr")
    REDIS_PASS: str | None = Field(alias="RedisPassword", default=None)
    REDIS_DB: int = Field(alias="RedisDb", default=0)
    POOL_SIZE: int = Field(alias="PoolSize", default=10)

    @property
    def REDIS_URL(self) -> str:
        # Формат: redis://[:password]@host:port/db
        return f"redis://{self.REDIS_PASS}{self.REDIS_ADDR}/{self.REDIS_DB}"

class MinIOSettings(BaseSettings):
    MINIO_ENDPOINT: str = Field(alias="MINIO_ENDPOINT", default="localhost:9000")
    MINIO_ADMIN: str = Field(alias="MINIO_ADMIN", default="minioadmin")
    MINIO_PASS: str = Field(alias="MINIO_PASS", default="minioadmin")
    MINIO_SSL: bool = Field(alias="MINIO_USE_SSL", default=False)
    CHAT_BUCKET_NAME: str = Field(alias="CHAT_BUCKET_NAME", default="chat")

class AuthJWT(BaseSettings):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14

# default_factory - позволяет создавать модели при init, чтобы создавать Settings(),
# который по дефолту не работает как factory (перестал почему то).
class Settings(BaseSettings):
    db: DbSettings = Field(alias="postgres", default_factory=lambda: DbSettings.model_construct())
    auth_jwt: AuthJWT = AuthJWT()
    redis: RedisSettings = Field(alias="redis", default_factory=lambda: RedisSettings.model_construct())
    minio: MinIOSettings = Field(default_factory=MinIOSettings)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, YamlConfigSettingsSource(settings_cls), env_settings

settings = Settings()