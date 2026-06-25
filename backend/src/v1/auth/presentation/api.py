from typing import Annotated

from dishka import FromDishka
from fastapi import APIRouter, Depends, Form, HTTPException, Header, Request, status

from dishka.integrations.fastapi import FromDishka, inject
from fastapi.security import HTTPBearer

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.core.utils.jwt_service.jwt_service import TokenData
from backend.src.v1.auth.domain.interfaces import ITokenAuth, ITokenProvider

router = APIRouter()

user_router = APIRouter()

# РКН заблокировал возможности интеграции бэкенда и фронтенда. Появляется легаси код из других проектов, где токены принимали через хедер.
security_bearer = HTTPBearer()
@inject
async def get_current_user_payload(
    #credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_bearer)],
    provider_service: FromDishka[ITokenProvider],
    auth_service: FromDishka[ITokenAuth],
    auth_header: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict:
    try:
        # validate_token выбросит HTTPException(401), если токен отозван
        auth_header = auth_header.replace('Bearer ', '')
        payload = provider_service.extract_payload(auth_header)
        await auth_service.is_token_valid(auth_header)

        return payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

# Алиас для удобства
CurrentUserPayload = Annotated[dict, Depends(get_current_user_payload)]

# Авторизация по OAuth 2.1, при запросе открывается страница на любом устройстве и предоставляет форму для ввода данных.
# Происходит генерация и обмен кодами для дополнительной безопасности HTTPS протокола и т.д.
@router.get('/')
@inject
async def authorize(
    request: Request,
    client_id: str,
    redirect_uri: str,
    state: str,
    code_challenge: str,
    ):
    return #await get_login_page(request, client_id, redirect_uri, state, code_challenge)

# Эндпоинт для принятия данных
@router.post('/login')
@inject
async def login(
    username: str = Form(...),
    password: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    code_challenge: str = Form(...),
    state: str = Form(...),
):
    pass

# Эндпоинт выдачи токена
@router.post("/token")
@inject
async def post_token(
    code: str = Form(...),
    code_verifier: str = Form(...),
    client_id: str = Form(...),
    grant_type: str = Form("authorization_code"),
):
    pass

# Эндпоинт обновления токена
@router.post("/refresh")
@inject
async def refresh_tokens(
):
    pass

# Эндпоинт регистрации юзера
@router.post("/register")
@inject
async def register(
):
    pass

# Эндпоинт выхода конкретного юзера
@router.post("/logout")
@inject
async def logout(
    auth_header: Annotated[str | None, Header(alias="Authorization")] = None,
    x_refresh_token: Annotated[str | None, Header(alias="X-Refresh-Token")] = None,
    auth_service: FromDishka[ITokenAuth] = None
):
    if not auth_header or not x_refresh_token:
        raise HTTPException(status_code=401, detail="Missing tokens in headers")
    auth_header = auth_header.replace('Bearer ','')
    await auth_service.revoke_specific_session(auth_header, x_refresh_token)
    return {"detail": "Successfully logged out from current device"}

# Эндпоинт выхода со всех устройств
@router.post("/logout-all")
@inject
async def logout_all(
):
    pass

@router.post('/test-token', response_model=TokenData)
@inject
async def get_test_token(
    auth_provider: FromDishka[ITokenAuth]
):
    result = await auth_provider.set_tokens()
    return result

# ... CRUD для пользователя

@user_router.get("/me")
@inject
async def get_current_user_profile(
    payload: CurrentUserPayload,
    uow: FromDishka[IUnitOfWork]
):
    user_id = payload.get("sub")
    async with uow:
        result = await uow.users.get_user_by_id(user_id)
        if result:
            return result
        else:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@user_router.patch("/update")
async def update_user():
    #TODO реализовать эндпоинт для обновления данных пользователя (кроме пароля)
    pass

@user_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    #TODO реализовать эндпоинт для удаления пользователя по id, который будет требовать аутентификацию и проверку прав доступа.
    pass