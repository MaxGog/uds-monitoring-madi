from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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