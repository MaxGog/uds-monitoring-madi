import base64
import hashlib
import secrets
import sys

import pytest
from typing import AsyncIterator
from httpx import AsyncClient, ASGITransport
from dishka import FromDishka, make_async_container, AsyncContainer
from dishka.integrations.fastapi import inject
import asyncio
from backend.core.ioc.auth_ioc import AuthProvider
from backend.core.ioc.dbs_ioc import DbProvider
from backend.core.ioc.filesystem_ioc import FilesystemProvider
from backend.core.ioc.repo_ioc import RepoProvider
from backend.core.ioc.uc_ioc import UsecaseProvider
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IAuthUsecases, IUserRepo, IUserUsecases
from backend.src.v1.auth.presentation.dto.user_dto import UserCreateRequest
from main import create_app

@pytest.fixture(scope="session")
def test_container():
    """Создаем изолированный контейнер для тестов."""
    container = make_async_container(
        DbProvider(),
        AuthProvider(),
        FilesystemProvider(),
        RepoProvider(),
        UsecaseProvider()
    )
    return container

@pytest.fixture(scope="session", autouse=True)
def event_loop():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Фикстура для самого FastAPI приложения
@pytest.fixture(scope="session")
def app(test_container):
    container = make_async_container(
        DbProvider(), 
        AuthProvider(), 
        FilesystemProvider(), 
        RepoProvider(), 
        UsecaseProvider()
    )
    app_instance = create_app(container=container)
    return app_instance

# Фикстура асинхронного клиента для выполнения запросов/каждого теста
@pytest.fixture(scope="function")
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="function")
async def test_user(app):
    """Фикстура создает пользователя и сразу закрывает соединение."""
    container = app.state.dishka_container
    
    email = "real_test_user@madi.ru"
    plain_password = "RealSecurePassword123!"

    async with container() as request_container:
        user_uc = await request_container.get(IUserUsecases)
        auth_uc = await request_container.get(IAuthUsecases)
        # await auth_uc.register_new_user(...)

    yield {"email": email, "password": plain_password}

    async with container() as request_container:
        user_uc = await request_container.get(IUserUsecases)
        # await user_uc.hard_delete_user_by_email(...)

@pytest.fixture(scope="function")
async def auth_client(app, client: AsyncClient, test_user) -> AsyncClient:
    """Авторизует клиента без удержания контейнера Dishka."""
    container = app.state.dishka_container

    async with container() as request_container:
        auth_uc = await request_container.get(IAuthUsecases)
        verifier = secrets.token_urlsafe(64)
        sha256_hash = hashlib.sha256(verifier.encode('utf-8')).digest()
        challenge = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').rstrip('=')

        auth_code = await auth_uc.login(
            email=test_user["email"], 
            password=test_user["password"], 
            code_challenge=challenge
        )
        tokens = await auth_uc.exchange_code_for_tokens(
            code=auth_code, 
            code_verifier=verifier
        )

    client.headers["Authorization"] = f"Bearer {tokens.access_token}"
    client.cookies["refresh_token"] = tokens.refresh_token
    
    yield client

    client.headers.pop("Authorization", None)
    client.cookies.pop("refresh_token", None)
