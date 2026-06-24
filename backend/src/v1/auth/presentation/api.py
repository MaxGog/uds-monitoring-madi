from dishka import FromDishka
from fastapi import APIRouter, Form, Request
from dishka.integrations.fastapi import FromDishka, inject

from backend.core.utils.jwt_service.jwt_service import TokenData
from backend.src.v1.auth.domain.interfaces import ITokenAuth

router = APIRouter()

user_router = APIRouter()

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
):
    pass

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
):
    #TODO реализовать эндпоинт для получения данных о самом себе
    pass

@user_router.patch("/update")
async def update_user():
    #TODO реализовать эндпоинт для обновления данных пользователя (кроме пароля)
    pass

@user_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    #TODO реализовать эндпоинт для удаления пользователя по id, который будет требовать аутентификацию и проверку прав доступа.
    pass