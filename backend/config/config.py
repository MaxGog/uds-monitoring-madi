import logging
from pathlib import Path
from typing import Any, Dict, Literal, Self, Tuple, Type

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource
from sqlalchemy import URL
import yaml


BASE_DIR = Path(__file__).parent.parent

YAML_FILE_PATH = BASE_DIR / "config" / "config-local.yml"

class LoggerSettings(BaseModel):
    '''
    Здесь напрямую вызываются поля из YAML без алиасов
    В качестве примера конфигурирования.
    '''
    development: bool
    disable_caller: bool = Field(alias="disableCaller")
    disable_stacktrace: bool = Field(alias="disableStacktrace")
    encoding: Literal["console", "json"]
    level: str
    # AIOREDIS_LOGGING: bool = Field(alias="aioredis_logging", default = True) 
    # UVICORN_LOGGING: bool = Field(alias="uvicorn_logging", default = True)
    #SQLALCHEMY_LOGGING: bool = Field(alias = "sqlalchemy_logging", default = False)
    # PROTOCOL_LOGGING: bool = Field(alias="protocol_logging", default = True)

class DbSettings(BaseModel):
    DB_HOST: str = Field(alias="pgHost")
    DB_PORT: int = Field(alias="pgPort")
    DB_USER: str = Field(alias="pgUser")
    DB_PASS: str = Field(alias="pgPassword")
    DB_NAME: str = Field(alias="pgDbName")
    DB_DRIVER: str = Field(alias="pgDriver")
    SSL_MODE: bool = Field(alias="pgSsl")
    LOGGING: bool = Field(alias="pgLogging")
    
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
    def ECHO(self) -> bool: return self.LOGGING
    @property
    def ECHO_POOL(self) -> bool: return self.LOGGING
    @property
    def POOL_PRE_PING(self) -> bool: return True
    @property
    def POOL_SIZE(self) -> int: return 10
    
    
    #f"postgresql+asyncpg://my_admin:secret@localhost/app_db"

class RedisSettings(BaseModel):
    REDIS_ADDR: str = Field(alias="redisAddr")
    REDIS_PASS: str = Field(alias="redisPassword")
    REDIS_DB: int = Field(alias="redisDb")
    POOL_SIZE: int = Field(alias="poolSize")

    @property
    def REDIS_URL(self) -> str:
        # Формат: redis://[:password]@host:port/db
        return f"redis://:{self.REDIS_PASS}@{self.REDIS_ADDR}/{self.REDIS_DB}"

class MinIOSettings(BaseModel):
    MINIO_ENDPOINT: str = Field(alias = "minioEndpoint")
    MINIO_ADMIN: str = Field(alias = "minioAccessKey")
    MINIO_PASS: str = Field(alias = "minioSecretKey")
    MINIO_SSL: bool = Field(alias = "useSSL")
    FILE_BUCKET_NAME: str = Field(alias = "fileBucketName")

class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "ec256-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "ec256-public.pem"
    algorithm: str = "ES256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14

class SSL(BaseModel):
    enabled: bool
    cert_file: str
    key_file: str

    # model_validator проверяет наличие файлов если SSL включён
    @model_validator(mode='after')
    def validate_ssl_files(self) -> Self:
        # Если SSL выключен, проверять файлы не нужно
        if not self.enabled:
            return self
        
        # Если включен, проверяем пути
        cert_path = BASE_DIR / "core" / "utils" / "ssl" / self.cert_file
        key_path = BASE_DIR / "core" / "utils" / "ssl" / self.key_file
        
        if not cert_path.exists():
            raise ValueError(f"SSL enabled, but cert_file not found at: {cert_path}")
        
        if not key_path.exists():
            raise ValueError(f"SSL enabled, but key_file not found at: {key_path}")
            
        return self
    
    #field_validator находит в папке core/utils/ssl нужные сертификаты и создаёт из них объект Path, который затем уходит в main.py
    @field_validator("cert_file", "key_file")
    @classmethod
    def assemble_path(cls, v: str) -> Path:
        # v - это значение из YAML (например, "server.crt")
        path = BASE_DIR / "core" / "utils" / "ssl" / v
        return path

class ApiServer(BaseModel):
    host: str
    port: int
    mode: str
    ssl: SSL
    csrf: bool
    cookie_name: str = Field(alias="cookie-name")

class Settings(BaseSettings):
    server: ApiServer = Field(alias="server")
    db: DbSettings = Field(alias="postgres")
    auth_jwt: AuthJWT = AuthJWT()
    redis: RedisSettings = Field(alias="redis")
    minio: MinIOSettings = Field(alias="aws")
    logger: LoggerSettings = Field(alias="logger")

    model_config = SettingsConfigDict(yaml_file=YAML_FILE_PATH)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
    
settings = Settings() # type: ignore
