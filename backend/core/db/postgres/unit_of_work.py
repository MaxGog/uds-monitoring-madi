from abc import abstractmethod
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


# Автоматический хелпер для работы с асинхронными транзакциями через контекстный менеджер. Сразу через интерфейс.

class IUnitOfWork(Protocol):
    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    async def __aexit__(self, *args): ...

class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        #self.users = PGUserRepository(session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # При ошибке автоматически откатывает транзакцию.
            await self.rollback()
        else:
            pass


    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.rollback()