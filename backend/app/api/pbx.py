"""HTTP: список узлов, снимок здоровья, журнал аварий."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas.pbx import AlarmListResponse, PbxHealthResponse, PbxListResponse
from app.services.health_repo import HealthRepository, SqlHealthRepository

router = APIRouter(tags=["pbx"])


async def get_health_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> HealthRepository:
    return SqlHealthRepository(session)


@router.get("/pbx", response_model=PbxListResponse)
async def list_pbx(
    repo: Annotated[HealthRepository, Depends(get_health_repo)],
) -> dict[str, Any]:
    items = await repo.list_nodes()
    return {"items": items}


@router.get("/pbx/{node_id}/health", response_model=PbxHealthResponse)
async def get_pbx_health(
    node_id: int,
    repo: Annotated[HealthRepository, Depends(get_health_repo)],
) -> dict[str, Any]:
    row = await repo.get_node_health(node_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": "PBX node not found"},
        )
    return row


@router.get("/alarms", response_model=AlarmListResponse)
async def list_alarms(
    repo: Annotated[HealthRepository, Depends(get_health_repo)],
    severity: str | None = None,
    open_: Annotated[bool | None, Query(alias="open")] = None,
    from_: Annotated[datetime | None, Query(alias="from")] = None,
    to: datetime | None = None,
) -> dict[str, Any]:
    items = await repo.list_alarms(severity=severity, open=open_, **{"from": from_, "to": to})
    return {"items": items, "total": len(items)}
