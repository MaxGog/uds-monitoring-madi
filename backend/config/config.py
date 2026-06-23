from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent

class DbSettings(BaseSettings):
    DB_USER: str = Field(alias="DB_USER")
    DB_PASS: str = Field(alias="DB_PASS")
    DB_NAME: str = Field(alias="DB_NAME")
    DB_DRIVER: str = Field(alias="DB_DRIVER")
    DB_HOST: str = Field(alias="DB_HOST")
    DB_PORT: int = Field(alias="DB_PORT")

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra = "ignore"
    )
    
    @property
    def DB_URL(self) -> str:
        url = URL.create(
            drivername=self.DB_DRIVER,
            database=self.DB_NAME,
            host=self.DB_HOST,
            port=self.DB_PORT,
            username=self.DB_USER,
            password=self.DB_PASS,
        ).render_as_string(hide_password=False)
        return(url)
    
    @property
    def ECHO(self) -> bool:
        return True
    
    @property
    def ECHO_POOL(self) -> bool:
        return True
    
    @property
    def POOL_PRE_PING(self) -> bool:
        return True
    
    @property
    def POOL_SIZE(self) -> int:
        return 10
    
    
    #f"postgresql+asyncpg://my_admin:secret@localhost/app_db"

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

class MinIOSettings(BaseSettings):
    MINIO_ENDPOINT: str = Field(alias="MINIO_ENDPOINT")
    MINIO_ADMIN: str = Field(alias="MINIO_ADMIN")
    MINIO_PASS: str = Field(alias="MINIO_PASS")
    MINIO_SSL: bool = Field(alias="MINIO_USE_SSL")
    CHAT_BUCKET_NAME: str = Field(alias="CHAT_BUCKET_NAME")
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra = "ignore"
    )

class AuthJWT(BaseSettings):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()
    redis: RedisSettings = RedisSettings()
    minio: MinIOSettings = MinIOSettings()


settings = Settings()