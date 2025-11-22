from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.entrypoints.api.locations import router as locations_router
from app.infrastructure.db.session import init_db


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.include_router(locations_router)


@app.get("/health", tags=["health"])  # simple health check endpoint
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
