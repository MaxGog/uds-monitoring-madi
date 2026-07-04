from abc import abstractmethod
from typing import Protocol


# Интерфейсы, можно легко подменять реализации и мокать

class IUserRepo(Protocol):
    ...

class IUserUsecases(Protocol):
    ...

class ITokenProvider(Protocol):
    @abstractmethod
    def create_access_token() -> str:
        pass

    @abstractmethod
    def create_refresh_token() -> str:
        pass
    ...

class ITokenStorage(Protocol):
    ...

class ITokenAuth(Protocol):
    ...

class IAuthUsecases(Protocol):
    ...

class IPasswordHasher(Protocol):
    ...

