import logging

from dishka import make_async_container
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from types_aiobotocore_s3 import S3Client
import uvicorn

from backend.core.db.redis.redis_conn import check_redis_connection
from backend.core.ioc.auth_ioc import AuthProvider
from backend.core.ioc.dbs_ioc import DbProvider
from backend.core.ioc.filesystem_ioc import FilesystemProvider
from backend.core.ioc.repo_ioc import RepoProvider
from backend.core.ioc.uc_ioc import UsecaseProvider
from backend.core.utils.csrf.csrf import CsrfSettings
from backend.core.utils.logger.app_logger import setup_logger
from backend.src.v1.auth.presentation.api import router as auth_router
from backend.src.v1.auth.presentation.user_api import router as user_router
from backend.src.v1.auth.presentation.role_api import router as role_router
from backend.src.v1.filesystem.presentation.api import router as fs_router
from backend.src.v1.data.presentation.tasks_api import router as task_router
from backend.src.v1.data.presentation.acts_api import router as act_router
from backend.src.v1.data.presentation.objects_monitoring_api import router as object_router
from backend.src.v1.data.presentation.roadmap_api import router as roadmap_router
from backend.src.v1.data.presentation.work_status_api import router as work_router


from backend.core.db.postgres.postgres_conn import db_engine, check_db_connection
from backend.core.db.redis.redis_conn import redis_client
from backend.core.db.aws.minio_conn import check_aws_connection
from backend.config.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    await check_db_connection(db_engine)
    await check_redis_connection(redis_client)
    client = await container().get(S3Client)
    await check_aws_connection(client)
    yield

    await db_engine.dispose()

logger = logging.getLogger(__file__)

app = FastAPI(lifespan=lifespan)


# Порядок вызовов функционала влияет
@CsrfProtect.load_config
def get_csrf_settings():
    return CsrfSettings()

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

origins = [
    "http://localhost:4000",
    "http://127.0.0.1:4000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=auth_router, prefix="/auth", tags=['auth'])
app.include_router(router=user_router, prefix='/users', tags=['user'])
app.include_router(router=fs_router, prefix="/fs", tags=['fs'])
app.include_router(router=task_router, prefix = "/task", tags = ['task'])
app.include_router(router=object_router, prefix = "/object", tags = ['object'])
app.include_router(router=roadmap_router, prefix = "/roadmap", tags = ['roadmap'])
app.include_router(router=act_router, prefix = "/act", tags = ['act'])
app.include_router(router=work_router, prefix = "/work", tags = ['work'])
app.include_router(router=role_router, prefix = "/role", tags = ['role'])

container = make_async_container(DbProvider(), AuthProvider(), FilesystemProvider(), RepoProvider(), UsecaseProvider())
setup_dishka(container, app)

if __name__ == "__main__":
    run_args = {
        "app": "main:app",
        "host": settings.server.host,
        "port": settings.server.port,
    }
    if settings.server.ssl.enabled:
        run_args.update({
            "ssl_keyfile": settings.server.ssl.key_file,
            "ssl_certfile": settings.server.ssl.cert_file,
        })
    logger.info('Start')
    uvicorn.run(
        reload=True,
        log_level="debug",
        reload_excludes=["*.log", "app.log"],
        **run_args
        #loop="asyncio"
        #log_config=None
    )