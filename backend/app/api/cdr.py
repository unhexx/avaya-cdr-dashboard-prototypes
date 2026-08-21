"""HTTP: список/деталь/экспорт CDR, ingest фикстур, mock-generate."""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.pbx import get_health_repo
from app.db import get_session
from app.services.cdr_ingest import generate_mock_cdrs, ingest_fixtures
from app.services.cdr_repo import CdrRepository, SqlCdrRepository
from app.services.health_ingest import ingest_health_fixtures
from app.services.health_repo import HealthRepository
from app.services.logs import ingest_log_fixtures
from app.services.recordings import get_default_recordings_service

router = APIRouter(tags=["cdr"])


class CdrPage(BaseModel):
    items: list[dict[str, Any]]
    page: int
    page_size: int
    total: int
    summary: dict[str, int]


class IngestResult(BaseModel):
    inserted: int
    skipped: int
    total: int
    parsed: int = 0
    nodes: int = 0
    snapshots: int = 0
    alarms: int = 0
    logs: int = 0
    logs_sip: int = 0
    logs_e1: int = 0
    logs_alarm: int = 0
    recordings: int = 0


async def get_cdr_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CdrRepository:
    return SqlCdrRepository(session)


@router.get("/cdr", response_model=CdrPage)
async def list_cdr(
    repo: Annotated[CdrRepository, Depends(get_cdr_repo)],
    from_: Annotated[datetime | None, Query(alias="from")] = None,
    to: datetime | None = None,
    direction: str | None = None,
    disposition: str | None = None,
    calling_number: str | None = None,
    dialed_number: str | None = None,
    match: Literal["contains", "exact", "prefix"] = "contains",
    agent_extension: str | None = None,
    vdn: str | None = None,
    trunk: str | None = None,
    account_code: str | None = None,
    q: str | None = None,
    sort: str = "-start_time",
    page: int = 1,
    page_size: int = 25,
) -> dict[str, Any]:
    return await repo.list_page(
        **{
            "from": from_,
            "to": to,
            "direction": direction,
            "disposition": disposition,
            "calling_number": calling_number,
            "dialed_number": dialed_number,
            "match": match,
            "agent_extension": agent_extension,
            "vdn": vdn,
            "trunk": trunk,
            "account_code": account_code,
            "q": q,
            "sort": sort,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/cdr/{cdr_id}")
async def get_cdr(
    cdr_id: int,
    repo: Annotated[CdrRepository, Depends(get_cdr_repo)],
) -> dict[str, Any]:
    row = await repo.get(cdr_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": "CDR record not found"},
        )
    return row


@router.get("/export")
async def export_cdr(
    repo: Annotated[CdrRepository, Depends(get_cdr_repo)],
    format: Literal["csv", "json"] = "csv",
    direction: str | None = None,
    disposition: str | None = None,
    q: str | None = None,
) -> Response:
    rows = await repo.export_rows(direction=direction, disposition=disposition, q=q)
    if format == "json":
        import json

        body = json.dumps(rows, ensure_ascii=False)
        return Response(content=body, media_type="application/json")
    if not rows:
        return Response(content="", media_type="text/csv")
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cdr.csv"},
    )


@router.get("/stats")
async def cdr_stats(repo: Annotated[CdrRepository, Depends(get_cdr_repo)]) -> dict[str, Any]:
    page = await repo.list_page(page=1, page_size=1)
    return {"total": page["total"], "talk_seconds": page["summary"]["talk_seconds"]}


@router.post("/ingest/fixtures", response_model=IngestResult)
async def post_ingest_fixtures(
    repo: Annotated[CdrRepository, Depends(get_cdr_repo)],
    health_repo: Annotated[HealthRepository, Depends(get_health_repo)],
) -> dict[str, int]:
    stats = await ingest_fixtures(repo)
    health = await ingest_health_fixtures(health_repo)
    stats.update(health)
    stats.update(ingest_log_fixtures())
    rec_svc = get_default_recordings_service()
    stats["recordings"] = await rec_svc.load_fixtures()
    return stats


@router.post("/mock-generate", response_model=IngestResult)
async def post_mock_generate(
    repo: Annotated[CdrRepository, Depends(get_cdr_repo)],
    n: Annotated[int, Query(ge=1, le=10_000)] = 100,
) -> dict[str, int]:
    rows = generate_mock_cdrs(n)
    stats = await repo.insert_many(rows)
    stats["parsed"] = len(rows)
    return stats
