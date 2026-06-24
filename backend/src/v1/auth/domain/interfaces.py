from abc import abstractmethod
from typing import Protocol


# Интерфейсы, можно легко подменять реализации и мокать

class IUserRepository(Protocol):
    pass

class ITokenProvider(Protocol):
    @abstractmethod
    def create_access_token() -> str:
        pass

    @abstractmethod
    def create_refresh_token() -> str:
        pass

class ITokenStorage(Protocol):
    pass

class ITokenAuth(Protocol):
    async def set_tokens(self, user_id: int | None = None):
        pass

class IPasswordHasher(Protocol):
    pass

