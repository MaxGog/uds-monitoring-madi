import base64
import hashlib
import logging
import re
import secrets
from urllib.parse import urlparse, parse_qs
import pytest
from httpx import AsyncClient, ASGITransport

from backend.tests.conftest import app

logger = logging.getLogger(__file__)

# Хелпер для генерации PKCE (Code Verifier и Challenge)
def generate_pkce_pair():
    # Текст длиной от 43 до 128 символов
    # Хешируем через SHA-256
    # Кодируем в Base64 URL-safe без заполнения (=)
    verifier = secrets.token_urlsafe(64)
    sha256_hash = hashlib.sha256(verifier.encode('utf-8')).digest()
    challenge = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').rstrip('=')
    
    return verifier, challenge

@pytest.mark.asyncio(loop_scope="session")
async def test_successful_real_auth_flow(client: AsyncClient, test_user):
    """Честный сквозной тест авторизации без моков."""
    
    client_id = "web-platform-madi"
    redirect_uri = "http://localhost:3000/callback"
    code_verifier, code_challenge = generate_pkce_pair()
    logger.info('Test login page html response')
    auth_response = await client.get(
        "/auth/authorize",
        params={
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
    )
    assert auth_response.status_code == 200

    html_content = auth_response.text
    csrf_token_match = re.search(r'id="csrf_token"\s+value="([^"]+)"', html_content)
    assert csrf_token_match is not None, "CSRF токен не найден в HTML шаблоне"
    csrf_token = csrf_token_match.group(1)
    logger.info('Test submit login form')
    login_response = await client.post(
        "/auth/login-submit",
        data={
            "email": test_user["email"],
            "password": test_user["password"],
            "redirect_uri": redirect_uri,
            "code_challenge": code_challenge
        },
        headers={"X-CSRF-Token": csrf_token}
    )

    assert login_response.status_code == 200

    url_in_response = login_response.json()["url"]
    parsed_url = urlparse(url_in_response)
    query_params = parse_qs(parsed_url.query)
    
    assert "code" in query_params, f"Код авторизации не найден в ответе: {url_in_response}"
    auth_code = query_params["code"][0]
    logger.info('Test Token Exchange for Auth Code')
    token_response = await client.post(
        "/auth/token",
        data={
            "code": auth_code,
            "code_verifier": code_verifier
        }
    )
    
    assert token_response.status_code == 200
    token_json = token_response.json()

    assert "access_token" in token_json
    real_access_token = token_json["access_token"]
    assert len(real_access_token) > 20

    assert "refresh_token" in client.cookies
    real_refresh_token = client.cookies["refresh_token"]
    logger.info('Test Refresh Logic')
    refresh_response = await client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {real_access_token}"}
    )
    
    assert refresh_response.status_code == 200
    refresh_json = refresh_response.json()
    
    assert "access_token" in refresh_json
    assert refresh_json["access_token"] != real_access_token