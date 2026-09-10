import asyncio
from urllib.parse import parse_qs, urlparse
import uuid

import pytest
import os
from pathlib import Path
from fastapi import status
from httpx import AsyncClient
import requests

from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest
from backend.src.v1.filesystem.domain.models import DocumentOwnerType
from backend.src.v1.filesystem.presentation.dtos import DocumentCreateRequest, DocumentUpdateRequest, GetUploadUrlRequest
from backend.config.config import settings

@pytest.fixture(scope="session", autouse=True)
def test_file():
    """Создает реальный файл на диске для теста."""
    assets_dir = Path(__file__).parent / "test_assets"
    assets_dir.mkdir(exist_ok=True)
    file_path = assets_dir / "cat.webp"
    yield file_path
# python -m pytest backend/tests/integration/test_document_crud.py
TARGET_CONTENT_TYPE = "image/webp"
TARGET_FILE_NAME = 'cat.webp'

@pytest.mark.asyncio(loop_scope="session")
async def test_document_s3_storage_crud_lifecycle(auth_client: AsyncClient, test_file: Path):
    # ------------------------------------------------------------------------
    # ШАГ 1: Запрос URL для загрузки файла (POST /fs/upload-url)
    # ------------------------------------------------------------------------
    upload_url_dto = GetUploadUrlRequest(
          name = TARGET_FILE_NAME,
          content_type = TARGET_CONTENT_TYPE,
          owner_type = DocumentOwnerType.CONTRACT,
          owner_id = 1,
    )

    upload_url_empty_file_dto = GetUploadUrlRequest(
          name = TARGET_FILE_NAME,
          content_type = TARGET_CONTENT_TYPE,
          owner_type = None,
          owner_id = None,
    )
    
    upload_data = BaseRequest(data = upload_url_dto).model_dump(mode='json')
    upload_empty_data = BaseRequest(data = upload_url_empty_file_dto).model_dump(mode='json')
    url_response = await auth_client.post("/fs/upload-url", json=upload_data)
    url_response_empty_data = await auth_client.post("/fs/upload-url", json=upload_empty_data)
    assert url_response.status_code == status.HTTP_200_OK
    assert url_response_empty_data.status_code == status.HTTP_200_OK

    url_json = url_response.json()
    assert "data" in url_json
    upload_url = url_json["data"]["upload_url"]
    s3_bucket = url_json["data"]["s3_bucket"]
    s3_key = url_json["data"]["s3_key"]
    

    upload_url_empty_data = url_response_empty_data.json()["data"]["upload_url"]
    s3_key_empty_data = url_response_empty_data.json()["data"]["s3_key"]

    parsed_url_empty = urlparse(upload_url_empty_data)
    query_params_empty = parse_qs(parsed_url_empty.query)

    headers_empty = {
        "Content-Type": TARGET_CONTENT_TYPE
    }
    for key, values in query_params_empty.items():
        if key.startswith("x-amz-meta-"):
            headers_empty[key] = values[0]

    if settings.minio.MINIO_SSL == False:
        assert url_json["data"]["upload_url"].startswith("http://")
    else:
        assert url_json["data"]["upload_url"].startswith("https://")
    assert s3_bucket == "files"
    assert s3_key is not None

    parsed_url = urlparse(upload_url)
    query_params = parse_qs(parsed_url.query)

    headers = {
        "Content-Type": TARGET_CONTENT_TYPE
    }
    for key, values in query_params.items():
        if key.startswith("x-amz-meta-"):
            headers[key] = values[0]
    # ------------------------------------------------------------------------
    # ШАГ 2: РЕАЛЬНАЯ ЗАГРУЗКА БИНАРНИКА В MINIO (PUT-запрос)
    # ------------------------------------------------------------------------
    file_bytes = test_file.read_bytes()
    expected_size = len(file_bytes)

    minio_put_empty = requests.put(
        upload_url_empty_data,
        data = file_bytes,
        headers = headers_empty,
    )

    minio_put_response = requests.put(
        upload_url, 
        data=file_bytes, 
        headers=headers
    )
    assert minio_put_response.status_code == status.HTTP_200_OK
    assert minio_put_empty.status_code == status.HTTP_200_OK
    await asyncio.sleep(2) # Ожидание отработки вебхука

    # ------------------------------------------------------------------------
    # ШАГ 3: Получение списка всех сохраненных документов (GET /fs/)
    # ------------------------------------------------------------------------

    list_response = await auth_client.get("/fs/")
    assert list_response.status_code == status.HTTP_200_OK
    
    list_json = list_response.json()
    assert len(list_json["data"]) > 0

    target_document = next(
        (item for item in list_json["data"] if item["s3_key"] == s3_key), 
        None
    )
    assert target_document is not None, f"Документ с s3_key {s3_key} не найден в БД. Возможно, вебхук не отработал."

    document_id = target_document["id"]

    # ------------------------------------------------------------------------
    # ШАГ 4: Получение информации о конкретном документе (GET /fs/{id})
    # ------------------------------------------------------------------------
    get_response = await auth_client.get(f"/fs/{document_id}")
    assert get_response.status_code == status.HTTP_200_OK
    
    get_json = get_response.json()
    assert get_json["data"]["id"] == document_id
    assert get_json["data"]["s3_key"] == s3_key
    assert get_json["data"]["size_bytes"] == expected_size

    # ------------------------------------------------------------------------
    # ШАГ 5: Получение ссылки на скачивание (GET /fs/{id}/download)
    # ------------------------------------------------------------------------

    download_response = await auth_client.get(f"/fs/{document_id}/download")
    
    # Проверяем структуру ответа
    assert download_response.status_code == status.HTTP_200_OK
    
    response_json = download_response.json()
    assert "data" in response_json
    
    download_url = response_json["data"]
    assert isinstance(download_url, str)
    assert download_url.startswith("http://") or download_url.startswith("https://")
    
    # Проверяем, что pre-signed ссылка от S3/MinIO содержит необходимые query-параметры для скачивания
    assert "Signature=" in download_url
    assert "AWSAccessKeyId=" in download_url or "X-Amz-Signature=" in download_url


    # ------------------------------------------------------------------------
    # ШАГ 6: Изменение имени документа/связи (PATCH /document/{id})
    # ------------------------------------------------------------------------
    update_dto = DocumentUpdateRequest(
        name="cat_final.webp",
        owner_id=999,
    )
    update_request = BaseRequest(data = update_dto).model_dump(mode = "json")
    update_response = await auth_client.patch(f"/fs/{document_id}", json=update_request)
    assert update_response.status_code == status.HTTP_200_OK
    
    update_json = update_response.json()
    assert update_json["data"]["name"] == "cat_final.webp"
    assert update_json["data"]["owner_id"] == 999
    assert update_json["data"]["s3_key"] == s3_key 

    # ------------------------------------------------------------------------
    # ШАГ 7: Удаление документа из БД и S3 (DELETE /document/{id})
    # ------------------------------------------------------------------------
    delete_response = await auth_client.delete(f"/fs/{document_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert delete_response.text == ""

    # ------------------------------------------------------------------------
    # ШАГ 8: Контрольная проверка отсутствия сущности (GET после DELETE)
    # ------------------------------------------------------------------------
    post_delete_response = await auth_client.get(f"/fs/{document_id}")
    assert post_delete_response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio(loop_scope="session")
async def test_get_download_url_not_found(auth_client: AsyncClient):
    """Проверка возврата 404 ошибки при запросе несуществующего file_id."""
    
    non_existent_id = uuid.uuid4()
    
    response = await auth_client.get(f"/fs/{non_existent_id}/download")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND