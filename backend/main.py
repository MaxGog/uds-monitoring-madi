from dishka import make_async_container
from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka
import uvicorn

from backend.src.v1.auth.presentation.api import router as auth_router
from backend.src.v1.filesystem.presentation.api import router as fs_router

app = FastAPI()

app.include_router(router=auth_router, prefix="/auth", tags=['auth'])
app.include_router(router=fs_router, prefix="/fs", tags=['fs'])

container = make_async_container(AuthProvider(), FsProvider())
setup_dishka(container, app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        log_level="debug",
        host = "0.0.0.0",
        port = 8000,
        reload_excludes=["*.log", "app.log"],
    )