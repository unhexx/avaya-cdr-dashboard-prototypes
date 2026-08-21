"""Точка входа FastAPI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.deps import optional_basic_auth
from app.api.health import router as health_router
from app.config import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Миграции гоняет compose-команда (alembic upgrade), не lifespan —
    # чтобы pytest не требовал живой PostgreSQL.
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Avaya CDR Dashboard",
        version=__version__,
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        dependencies=[Depends(optional_basic_auth)],
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:4173",
            "http://localhost:4173",
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router, prefix="/api")
    application.state.settings = settings
    return application


app = create_app()
