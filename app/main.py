import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIASGIMiddleware

from app.core.config import get_settings
from app.entrypoints.api.locations import router as locations_router
from app.entrypoints.api.internal_auth import require_internal_key
from app.entrypoints.api.limiter import limiter
from app.infrastructure.db.session import init_db


def _configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                }
            },
            "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
            "loggers": {
                "app": {"handlers": ["console"], "level": "INFO", "propagate": False},
            },
            "root": {"handlers": ["console"], "level": "WARNING"},
        }
    )


_configure_logging()

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


# debug=False siempre; la config puede controlar verbosidad de logging por separado
app = FastAPI(title=settings.app_name, debug=False, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIASGIMiddleware)
app.include_router(locations_router, dependencies=[Depends(require_internal_key)])


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger(__name__).error("Error no manejado en %s", request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor."})


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
