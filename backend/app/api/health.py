"""Liveness: всегда 200 при поднятом процессе, флаг fixtures обязателен."""

from typing import Literal

from fastapi import APIRouter

from app import __version__
from app.config import get_settings
from app.db import ping_database
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    ping = await ping_database()
    db_state: Literal["ok", "down"] = "ok" if ping == "ok" else "down"
    return HealthResponse(
        status="ok",
        version=__version__,
        fixtures=settings.use_fixtures,
        db=db_state,
    )
