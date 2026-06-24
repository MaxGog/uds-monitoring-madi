import logging

from dishka import make_async_container
from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka
from fastapi.concurrency import asynccontextmanager
import uvicorn

from backend.core.ioc.auth_ioc import AuthProvider
from backend.core.ioc.dbs_ioc import DbProvider
from backend.core.ioc.filesystem_ioc import FilesystemProvider
from backend.core.utils.logger.app_logger import setup_logger
from backend.src.v1.auth.presentation.api import router as auth_router
from backend.src.v1.auth.presentation.api import user_router
from backend.src.v1.filesystem.presentation.api import router as fs_router
from backend.core.db.postgres.postgres_conn import db_engine, check_db_connection



@asynccontextmanager
async def lifespan(app: FastAPI):
    result = await check_db_connection(db_engine)
    logger.info(f'Tested db conn: {result}')
    yield

    await db_engine.dispose()

setup_logger()
logger = logging.getLogger("backend")

app = FastAPI(lifespan=lifespan)


app.include_router(router=auth_router, prefix="/auth", tags=['auth'])
app.include_router(router=user_router, prefix='user', tags=['user'])
app.include_router(router=fs_router, prefix="/fs", tags=['fs'])

container = make_async_container(DbProvider(), AuthProvider(), FilesystemProvider())
setup_dishka(container, app)

if __name__ == "__main__":
    logger.info('Start')
    uvicorn.run(
        "main:app",
        reload=True,
        log_level="debug",
        host = "0.0.0.0",
        port = 8000,
        reload_excludes=["*.log", "app.log"],
    )