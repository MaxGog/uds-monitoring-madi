import base64
import hashlib
from pathlib import Path
import secrets
from typing import Annotated

from dishka import FromDishka
from fastapi import APIRouter, Depends, Form, HTTPException, Header, Request, status
from fastapi.templating import Jinja2Templates

from dishka.integrations.fastapi import FromDishka, inject
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer
from fastapi_csrf_protect import CsrfProtect

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.core.utils.jwt_service.jwt_service import TokenData
from backend.src.v1.auth.domain.interfaces import ITokenAuth, ITokenProvider

router = APIRouter()
user_router = APIRouter()

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
    csrf_protect: CsrfProtect = Depends()
):
    form_data = await request.form()
    email = form_data.get("email")
    password = form_data.get("password")
    redirect_uri = form_data.get("redirect_uri")
    code_challenge = form_data.get("code_challenge")

    await csrf_protect.validate_csrf(request)

    if email != "admin@madi.ru" and password != "secret":
         response = JSONResponse(
             content={"url":f"/auth/authorize?client_id=web-platform-madi&redirect_uri={redirect_uri}&code_challenge={code_challenge}&code_challenge_method=S256&error=1"},
             status_code=status.HTTP_302_FOUND
         )
         return response
    
    auth_code = secrets.token_urlsafe(32)
    auth_code = 123456789
    nuxt_callback_url = f"{redirect_uri}?code={auth_code}"

    response = JSONResponse(content={"url": nuxt_callback_url}, status_code=status.HTTP_200_OK)

    _, signed_token = csrf_protect.generate_csrf_tokens()
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response

# Эндпоинт выдачи токена
@router.post("/token")
@inject
async def exchange_code_for_token(
    code: str = Form(...),
    code_verifier: str = Form(...),
):
    print(code)
    print(code_verifier)
    print('EXCHANGING CODES FOR TOKEN')
    stored_data = '123456789:admin@madi.ru'
    saved_challenge, email = stored_data.split(":")
    challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    calculated_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').replace('=', '')
    calculated_challenge = 123456789
    saved_challenge = 123456789
    if calculated_challenge != saved_challenge:
        raise HTTPException(status_code=400, detail="Ошибка верификации PKCE")
    return {
        "access_token": "generated_access_jwt_token",
        "refresh_token": "generated_refresh_jwt_token",
        "user": {"id": 1, "email": email, "role": "admin"}
    }

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