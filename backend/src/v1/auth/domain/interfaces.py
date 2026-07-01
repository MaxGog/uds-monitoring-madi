from abc import abstractmethod
from typing import Protocol


# Интерфейсы, можно легко подменять реализации и мокать

class IUserRepo(Protocol):
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
    ...

class IAuthUsecases(Protocol):
    ...

class IPasswordHasher(Protocol):
    pass

