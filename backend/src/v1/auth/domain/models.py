from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import json

@dataclass
class UserModel:
    id: int
    username: str
    email: str

class UserRole(StrEnum):
    admin = "admin"
    viewer = "viewer"

class UserStatus(StrEnum):
    active = "active"
    blocked = "blocked"

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
    user_id: str
    challenge: str
    scope: str = "default"

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, data: str):
        return cls(**json.loads(data))
    
