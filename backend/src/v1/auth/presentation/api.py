from dishka import FromDishka
from fast_depends import inject
from fastapi import APIRouter, Form, Request


router = APIRouter()



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

# ... CRUD для пользователя

