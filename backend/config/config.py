from pathlib import Path
from typing import Any, Dict, Literal, Tuple, Type

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from sqlalchemy import URL
import yaml


BASE_DIR = Path(__file__).parent.parent

YAML_FILE_PATH = BASE_DIR / "config" / "config-local.yml"

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

class LoggerSettings(BaseModel):
    DEVELOPMENT: bool = Field(alias="Development", default=True)
    DISABLE_CALLER: bool = Field(alias="DisableCaller", default=False)
    DISABLE_STACKTRACE: bool = Field(alias="DisableStacktrace", default=False)
    ENCODING: Literal["console", "json"] = Field(alias="Encoding", default="console")
    LEVEL: str = Field(alias="Level", default="INFO")
    # AIOREDIS_LOGGING: bool = Field(alias="aioredis_logging", default = True) 
    # UVICORN_LOGGING: bool = Field(alias="uvicorn_logging", default = True)
    # SQLALCHEMY_LOGGING: bool = Field(alias = "sqlalchemy_logging", default = False)
    # PROTOCOL_LOGGING: bool = Field(alias="protocol_logging", default = True)

class DbSettings(BaseModel):
    DB_USER: str = Field(alias="PostgresqlUser")
    DB_PASS: str = Field(alias="PostgresqlPassword")
    DB_NAME: str = Field(alias="PostgresqlDbname")
    DB_DRIVER: str = Field(alias="PgDriver", default="postgresql+asyncpg")
    DB_HOST: str = Field(alias="PostgresqlHost")
    DB_PORT: int = Field(alias="PostgresqlPort")
    SSL_MODE: bool = Field(alias="PostgresqlSslmode")
    
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

class RedisSettings(BaseModel):
    REDIS_ADDR: str = Field(alias="RedisAddr")
    REDIS_PASS: str | None = Field(alias="RedisPassword", default = None)
    REDIS_DB: int = Field(alias="RedisDb", default=0)
    POOL_SIZE: int = Field(alias="PoolSize", default=10)

    @property
    def REDIS_URL(self) -> str:
        # Формат: redis://[:password]@host:port/db
        return f"redis://:{self.REDIS_PASS}@{self.REDIS_ADDR}/{self.REDIS_DB}"

class MinIOSettings(BaseModel):
    MINIO_ENDPOINT: str = Field(alias="MinioEndpoint", default="localhost:9000")
    MINIO_ADMIN: str = Field(alias="MinioAccessKey", default="minioadmin")
    MINIO_PASS: str = Field(alias="MinioSecretKey", default="minioadmin")
    MINIO_SSL: bool = Field(alias="UseSSL", default=False)

class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "ec256-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "ec256-public.pem"
    algorithm: str = "ES256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14

class Settings(BaseSettings):
    db: DbSettings = Field(alias="postgres")
    auth_jwt: AuthJWT = AuthJWT()
    redis: RedisSettings = Field(alias="redis")
    minio: MinIOSettings = Field(alias="aws")
    logger: LoggerSettings = Field(alias="logger", default_factory=LoggerSettings)
    
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

settings = Settings() # type: ignore