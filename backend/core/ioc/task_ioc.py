from dishka import Provider, Scope, provide

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.filesystem.infrastructure.parser_service.db_importer import DatabaseImporter


class TaskProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_db_importer(self, uow: IUnitOfWork) -> DatabaseImporter:
        return DatabaseImporter(uow=uow)