from pathlib import Path
from pydantic import Field
from sqlalchemy import URL
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