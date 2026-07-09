from abc import abstractmethod
from typing import List, Optional, Protocol
from uuid import UUID
import uuid

from backend.core.db.postgres.data_orms.document_orm import Document, DocumentOwnerType
from backend.src.v1.filesystem.presentation.dtos import ConfirmUploadRequest, DocumentResponse, GetUploadUrlRequest

class IAwsService(Protocol):
    @abstractmethod
    async def generate_url(self, ClientMethod: str, Params: dict, ExpiresIn: int):
        pass

    @abstractmethod
    async def generate_upload_url(self, s3_key: str, content_type: str, uploader_id: str, owner_type: str | None, owner_id: int | None) -> str:
        pass

    # @abstractmethod
    # async def generate_upload_url(self, s3_key: str, content_type: str, expires_minutes: int = 15) -> str:
    #     pass

    @abstractmethod
    async def generate_download_url(self, bucket: str, s3_key: str, expires_minutes: int = 60) -> str:
        pass

    @abstractmethod
    def get_object_stats(self, bucket: str, s3_key: str):
        pass

    @abstractmethod
    def delete_object(self, bucket: str, s3_key: str) -> None:
        pass

class IFileRepo(Protocol):
    @abstractmethod
    async def get_by_id(self, doc_id: UUID) -> Optional[Document]: pass
    
    @abstractmethod
    async def get_all(self, owner_type: Optional[str] = None, owner_id: Optional[int] = None) -> List[Document]: pass
    
    @abstractmethod
    async def add(self, document: Document) -> None: pass
    
    @abstractmethod
    async def delete(self, document: Document) -> None: pass

class IFsUsecases(Protocol):
    @abstractmethod
    async def initiate_upload(self, uploader_id: UUID, data: GetUploadUrlRequest) -> dict:
        pass
    
    @abstractmethod
    async def confirm_upload(self, data: ConfirmUploadRequest, uploader_id: uuid.UUID) -> dict:
        pass

    @abstractmethod
    async def get_document_download_link(self, item_id: uuid.UUID) -> str:
        pass

    @abstractmethod
    async def delete_document(self, item_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def get_file_by_id(self, item_id: uuid.UUID) -> DocumentResponse:
        pass

    @abstractmethod
    async def get_files(self, owner_type: Optional[DocumentOwnerType] = None, owner_id: Optional[int] = None) -> List[DocumentResponse]:
        pass

class IFileAuthUsecases(Protocol):
    ...