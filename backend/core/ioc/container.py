from dishka import make_async_container, make_container

from backend.core.ioc.auth_ioc import AuthProvider
from backend.core.ioc.dbs_ioc import DbProvider
from backend.core.ioc.filesystem_ioc import FilesystemProvider
from backend.core.ioc.repo_ioc import RepoProvider
from backend.core.ioc.task_ioc import TaskProvider
from backend.core.ioc.uc_ioc import UsecaseProvider


def create_app_container():
    return make_async_container(DbProvider(), AuthProvider(), FilesystemProvider(), RepoProvider(), UsecaseProvider())


def create_task_container():
    return make_async_container(DbProvider(), AuthProvider(), RepoProvider(), UsecaseProvider(), FilesystemProvider(), TaskProvider())