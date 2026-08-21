"""HTTP: поиск dialplan (longest-prefix) и синхронизация фикстур."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.services.dialplan import (
    DialplanRepository,
    SqlDialplanRepository,
    sync_dialplan_fixtures,
)

router = APIRouter(tags=["dialplan"])


class DialplanListResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int
    q: str = ""
    source: str | None = None


class DialplanSyncResult(BaseModel):
    inserted: int
    total: int
    parsed: int = 0
    by_source: dict[str, int] = Field(default_factory=dict)


async def get_dialplan_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DialplanRepository:
    return SqlDialplanRepository(session)


@router.get("/dialplan", response_model=DialplanListResponse)
async def list_dialplan(
    repo: Annotated[DialplanRepository, Depends(get_dialplan_repo)],
    q: Annotated[str, Query(description="Номер для longest-prefix")] = "",
    source: Annotated[
        str | None,
        Query(description="ars | dialplan | ipo_shortcode | ipo_ars"),
    ] = None,
) -> dict[str, Any]:
    items = await repo.list_entries(q=q, source=source)
    return {"items": items, "total": len(items), "q": q, "source": source}


@router.post("/dialplan/sync", response_model=DialplanSyncResult)
async def post_dialplan_sync(
    repo: Annotated[DialplanRepository, Depends(get_dialplan_repo)],
) -> dict[str, Any]:
    """Перечитать фикстуры ARS/IPO и заменить таблицу dialplan_entries."""
    return await sync_dialplan_fixtures(repo)
