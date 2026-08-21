"""Схемы узлов АТС, снимков здоровья и аварий."""

from typing import Any

from pydantic import BaseModel, Field


class PbxNodeOut(BaseModel):
    id: int
    name: str
    kind: str
    host: str | None = None
    enabled: bool = True
    status: str | None = None
    occupancy_pct: float | None = None
    open_alarms: int = 0
    taken_at: str | None = None


class PbxListResponse(BaseModel):
    items: list[PbxNodeOut]


class HealthSnapshotOut(BaseModel):
    id: int
    taken_at: str | None
    status: str
    occupancy_pct: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class AlarmOut(BaseModel):
    id: int
    pbx_node_id: int | None = None
    raised_at: str | None = None
    cleared_at: str | None = None
    severity: str
    code: str | None = None
    resource: str | None = None
    message: str
    raw: str | None = None


class PbxNodeDetail(BaseModel):
    id: int
    name: str
    kind: str
    host: str | None = None
    enabled: bool = True
    extra: dict[str, Any] = Field(default_factory=dict)


class PbxHealthResponse(BaseModel):
    node: PbxNodeDetail
    snapshot: HealthSnapshotOut | None = None
    alarms: list[AlarmOut] = Field(default_factory=list)


class AlarmListResponse(BaseModel):
    items: list[AlarmOut]
    total: int
