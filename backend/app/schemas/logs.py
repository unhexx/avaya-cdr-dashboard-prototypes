"""Схемы журнала syslog SIP / E1 / alarm."""

from pydantic import BaseModel, Field


class LogEventOut(BaseModel):
    id: int
    pbx_node_id: int | None = None
    kind: str
    event_time: str | None = None
    host: str | None = None
    severity: str | None = None
    call_id: str | None = None
    sip_method: str | None = None
    sip_response: int | None = None
    ds1_board: str | None = None
    alarm_type: str | None = None
    message: str
    raw: str | None = None


class LogListResponse(BaseModel):
    items: list[LogEventOut] = Field(default_factory=list)
    total: int = 0
