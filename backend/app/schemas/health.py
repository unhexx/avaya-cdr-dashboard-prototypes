"""Схема liveness /api/health."""

from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str
    fixtures: bool = Field(description="USE_FIXTURES: CI и демо без живой АТС")
    db: Literal["ok", "down", "skipped"]
