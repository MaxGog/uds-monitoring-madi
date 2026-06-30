from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class UserModel:
    id: int
    username: str
    email: str



@dataclass
class CodeData:
    '''
    PKCE flow
    Модель данных, необходимая для реализации безопасного обмена данными, как один из способов предотвращения перехвата данных.
    Клиент генерирует code verifier и хэширует его, сервер принимает код и сохраняет у себя в виде хэша code challenge (клиент сообщает как хэшировал).
    Сервер возвращает код авторизации.
    Клиент отправляет код авторизации и изначальный code verifier.
    Сервер хэширует code verifier и сравнивает с сохраненным code challenge.
    Выдаются токены если всё валидно.
    '''
    user_id: int
    challenge: str
    scope: str = "default"

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, data: str):
        return cls(**json.loads(data))
    
@dataclass
class LoginResultDTO:
    access_token: str
    refresh_token: str
    user: UserModel
