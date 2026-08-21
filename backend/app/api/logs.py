"""HTTP: журнал SIP / E1 / alarm из syslog-фикстур."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Query

from app.schemas.logs import LogListResponse
from app.services.logs import list_logs

router = APIRouter(tags=["logs"])


@router.get("/logs", response_model=LogListResponse)
async def get_logs(
    kind: Annotated[Literal["sip", "e1", "alarm"] | None, Query()] = None,
    from_: Annotated[datetime | None, Query(alias="from")] = None,
    to: datetime | None = None,
    q: str | None = None,
    call_id: str | None = None,
) -> dict[str, Any]:
    return list_logs(kind=kind, from_=from_, to=to, q=q, call_id=call_id)
