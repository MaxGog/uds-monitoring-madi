import uuid

from pydantic import BaseModel, Field

class FileCreateResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    s3_key: str
    content_type: str
    

class UploadLinkRequest(BaseModel):
    filename: str = Field(..., description="Оригинальное имя файла с расширением")
    content_type: str = Field(..., description="MIME-тип файла, например, 'application/pdf'")

class UploadLinkResponse(BaseModel):
    file_id: str = Field(..., description="UUID файла, созданный в нашей системе")
    upload_url: str = Field(..., description="Временная PUT-ссылка для загрузки файла напрямую в MinIO")

class DownloadLinkResponse(BaseModel):
    download_url: str = Field(..., description="Временная GET-ссылка для скачивания файла")