import base64
from enum import Enum
import hashlib
import logging
from pathlib import Path
import secrets
import time
from typing import Annotated, List

from dishka import FromDishka
from fastapi import APIRouter, Cookie, Depends, Form, HTTPException, Header, Query, Request, Response, status
from fastapi.templating import Jinja2Templates

from dishka.integrations.fastapi import FromDishka, inject
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_csrf_protect import CsrfProtect

from backend.core.utils.jwt_service.jwt_service import TokenData
from backend.src.v1.auth.domain.interfaces import IAuthUsecases, ITokenAuth, ITokenProvider, IUserUsecases
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest, BaseResponse, UserCreateDTO, UserResponseDTO, UsersListResponse
from backend.config.config import settings

router = APIRouter()
user_router = APIRouter()

security_bearer = HTTPBearer()

access_token_scheme = HTTPBearer(
    bearerFormat="JWT",
)

refresh_token_scheme = HTTPBearer(
    bearerFormat="JWT"
)

logger = logging.getLogger(__file__)

class GrantTypes(str, Enum):
    AUTHORIZE = "authorize_code"
    PKCE = "pkce"
    CREDENTIALS = "credentials"
    DEVICE = "device"
    REFRESH = "refresh_token"

@inject
async def get_current_user_payload(
    provider_service: FromDishka[ITokenProvider],
    auth_service: FromDishka[ITokenAuth],
    auth_header: Annotated[HTTPAuthorizationCredentials, Depends(access_token_scheme)],
):
    try:
        # validate_token выбросит HTTPException(401), если токен отозван
        token = auth_header.credentials
        payload = provider_service.extract_payload(token)
        await auth_service.is_token_valid(token)

        return payload
    except HTTPException as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

# Алиас для удобства
CurrentUserPayload = Annotated[dict, Depends(get_current_user_payload)]

# Авторизация по OAuth 2.1, при запросе открывается страница на любом устройстве и предоставляет форму для ввода данных.
# Происходит генерация и обмен кодами для дополнительной безопасности HTTPS протокола и т.д.
@router.get('/authorize')
@inject
async def authorize(
    request: Request,
    client_id: str,
    redirect_uri: str,
    code_challenge: str,
    code_challenge_method: str,
    csrf_protect: CsrfProtect = Depends()
    ):
    if (client_id != "web-platform-madi"):
        raise HTTPException(status_code=400, detail="Invalid client_id")
    if code_challenge_method != "S256":
        raise HTTPException(status_code=400, detail="Unsupported challenge method")
    
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()

    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
    TEMPLATES_DIR = BASE_DIR / "templates"
    
    response = Jinja2Templates(directory=str(TEMPLATES_DIR)).TemplateResponse(
        request=request,
        name="login_form.html",
        context = {
        "request": request,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_challenge": code_challenge,
        "csrf_token": csrf_token,
    })
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response

# Эндпоинт для принятия данных
@router.post('/login-submit')
@inject
async def login(
    request: Request,
    uc: FromDishka[IAuthUsecases],
    csrf_protect: CsrfProtect = Depends()
):
    form_data = await request.form()
    email = str(form_data.get("email"))
    password = str(form_data.get("password"))
    redirect_uri = form_data.get("redirect_uri")
    code_challenge = str(form_data.get("code_challenge"))
    await csrf_protect.validate_csrf(request)

    result = await uc.login(email = email, password = password, code_challenge = code_challenge)

    if result == None:
        response = JSONResponse(
             content={"url":f"/auth/authorize?client_id=web-platform-madi&redirect_uri={redirect_uri}&code_challenge={code_challenge}&code_challenge_method=S256&error=1"},
             status_code=status.HTTP_302_FOUND
         )
        return response
    nuxt_callback_url = f"{redirect_uri}?code={result}"
    response = JSONResponse(content={"url": nuxt_callback_url}, status_code=status.HTTP_200_OK)

    _, signed_token = csrf_protect.generate_csrf_tokens()
    csrf_protect.set_csrf_cookie(signed_token, response)

    return response

# Эндпоинт выдачи токена
@router.post("/token")
@inject
async def exchange_code_for_token(
    uc: FromDishka[IAuthUsecases],
    response: Response,
    code: str = Form(...),
    code_verifier: str = Form(...),
    #grant_type: str = Form("authorization_code"),
):
    tokens = await uc.exchange_code_for_tokens(code, code_verifier)
    response.set_cookie(
        key = settings.server.cookie_name,
        value = tokens.refresh_token,
        httponly = True,
        samesite = 'lax',
        max_age = settings.auth_jwt.refresh_token_expire_days * 24 * 60 * 60,
        secure = settings.server.ssl
    )
    return { "access_token": tokens.access_token }


# Эндпоинт обновления токена
@router.post("/refresh")
@inject
async def refresh_tokens(
    uc: FromDishka[IAuthUsecases],
    response: Response,
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(access_token_scheme)],
    #refresh_token: str = Header(..., alias="X-Refresh-Token"),
    refresh_token: str = Cookie(None),
):
    logger.info(f'Trying to refresh token')
    if not refresh_token or not access_token:
        raise HTTPException(status_code=401, detail="Missing tokens")
    new_tokens = await uc.rotate_tokens(refresh_token = refresh_token, access_token = access_token.credentials)
    response.set_cookie(
        key = settings.server.cookie_name,
        value = new_tokens.refresh_token,
        httponly = True,
        samesite = 'lax',
        max_age = settings.auth_jwt.refresh_token_expire_days * 24 * 60 * 60,
        secure = settings.server.ssl
    )
    return { "access_token": new_tokens.access_token }

# Эндпоинт регистрации юзера
@router.post("/register")
@inject
async def register(
    data: BaseRequest[UserCreateDTO],
    uc: FromDishka[IAuthUsecases]
):
    result = await uc.register_new_user(data)
    return result

# Эндпоинт выхода конкретного юзера
@router.post("/logout")
@inject
async def logout(
    auth_service: FromDishka[ITokenAuth],
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(access_token_scheme)],
    x_refresh_token: str = Header(..., alias="X-Refresh-Token"),
):
    if not access_token or not x_refresh_token:
        raise HTTPException(status_code=401, detail="Missing tokens in headers")

    await auth_service.revoke_specific_session(access_token.credentials, x_refresh_token)
    return {"detail": "Successfully logged out current session"}

# Эндпоинт выхода со всех устройств
@router.post("/logout-all")
@inject
async def logout_all(
):
    pass

@router.post('/test-token', response_model=TokenData, tags=["dev-tools"])
@inject
async def get_test_token(
    auth_provider: FromDishka[ITokenAuth],
    role: str = Query(default = 'admin'),
):
    if role == 'admin':
        result = await auth_provider.set_tokens(user_id = '019f17ea-a900-7fe9-b66f-43d82725afca') # беру напрямую из бд
    elif role == 'viewer':
        result = await auth_provider.set_tokens(user_id = '019f17eb-219a-7f4d-a5ad-124044d79754')
    return result

# ... CRUD для пользователя

# Эндпоинт админа, который создаёт юзеров сам, передавая токены
@user_router.post("/", response_model=BaseResponse[UserResponseDTO])
@inject
async def create_user(
    current_user: CurrentUserPayload,
    payload: BaseRequest[UserCreateDTO],
    uc: FromDishka[IUserUsecases],
):
    user_id = str(current_user.get('sub'))
    data = payload.data
    try:
        result = await uc.create_user(creator_id = user_id, data = data)
        return {"data": result}
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't create new user")


@user_router.get("/me", response_model=UserResponseDTO)
@inject
async def get_current_user_profile(
    current_user: CurrentUserPayload,
    uc: FromDishka[IUserUsecases],
):
    user_id = str(current_user.get('sub'))
    try:
        result = await uc.get_me(user_id)
        return result
    except HTTPException as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@user_router.get('/', response_model=BaseResponse[List[UserResponseDTO]])
@inject
async def get_users(
    current_user: CurrentUserPayload,
    uc: FromDishka[IUserUsecases]
):
    user_id = str(current_user.get('sub'))
    try:
        result = await uc.get_users(user_id = user_id)
        return { "data": result }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting users")

# TODO реализовать нижестоящие эндпоинты
@user_router.get('/{user_id}', response_model=BaseResponse[UserResponseDTO])
@inject
async def get_user(
    current_user: CurrentUserPayload,
):
    pass

@user_router.patch("/{user_id}", response_model=BaseResponse[UserResponseDTO])
async def update_user(
    current_user: CurrentUserPayload
):
    #TODO реализовать эндпоинт для обновления данных пользователя (кроме пароля)
    pass

@user_router.delete("/{user_id}", response_model=BaseResponse[UserResponseDTO])
async def delete_user(
    current_user: CurrentUserPayload,
    user_id: str
    ):
    #TODO реализовать эндпоинт для удаления пользователя по id, который будет требовать аутентификацию и проверку прав доступа.
    pass

