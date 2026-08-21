"""Репозиторий узлов АТС, снимков и аварий (SQL и in-memory)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health import Alarm, HealthSnapshot
from app.models.pbx import PbxNode


def _dec(value: Decimal | float | int | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


class HealthRepository(Protocol):
    async def upsert_node(
        self, name: str, kind: str, host: str | None, extra: dict[str, Any]
    ) -> dict[str, Any]: ...

    async def insert_snapshot(
        self,
        pbx_node_id: int,
        taken_at: datetime,
        status: str,
        occupancy_pct: Decimal | float | None,
        details: dict[str, Any],
    ) -> dict[str, Any]: ...

    async def insert_alarm(
        self,
        pbx_node_id: int,
        raised_at: datetime,
        severity: str,
        code: str | None,
        resource: str | None,
        message: str,
        raw: str | None,
    ) -> dict[str, Any] | None: ...

    async def list_nodes(self) -> list[dict[str, Any]]: ...

    async def get_node_health(self, node_id: int) -> dict[str, Any] | None: ...

    async def list_alarms(self, **filters: Any) -> list[dict[str, Any]]: ...


def _node_out(
    node: dict[str, Any],
    *,
    status: str | None = None,
    occupancy_pct: float | None = None,
    open_alarms: int | None = None,
    taken_at: str | None = None,
) -> dict[str, Any]:
    return {
        "id": node["id"],
        "name": node["name"],
        "kind": node["kind"],
        "host": node.get("host"),
        "enabled": node.get("enabled", True),
        "status": status,
        "occupancy_pct": occupancy_pct,
        "open_alarms": open_alarms if open_alarms is not None else 0,
        "taken_at": taken_at,
    }


def _alarm_out(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "pbx_node_id": row.get("pbx_node_id"),
        "raised_at": _iso(row["raised_at"])
        if isinstance(row.get("raised_at"), datetime)
        else row.get("raised_at"),
        "cleared_at": _iso(row["cleared_at"])
        if isinstance(row.get("cleared_at"), datetime)
        else row.get("cleared_at"),
        "severity": row["severity"],
        "code": row.get("code"),
        "resource": row.get("resource"),
        "message": row["message"],
        "raw": row.get("raw"),
    }


class SqlHealthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_node(
        self, name: str, kind: str, host: str | None, extra: dict[str, Any]
    ) -> dict[str, Any]:
        existing = (
            await self._session.execute(select(PbxNode).where(PbxNode.name == name))
        ).scalar_one_or_none()
        if existing is not None:
            existing.kind = kind
            existing.host = host
            existing.extra = extra
            existing.enabled = True
            await self._session.commit()
            await self._session.refresh(existing)
            return {
                "id": existing.id,
                "name": existing.name,
                "kind": existing.kind,
                "host": existing.host,
                "enabled": existing.enabled,
                "created": False,
            }
        node = PbxNode(name=name, kind=kind, host=host, enabled=True, extra=extra)
        self._session.add(node)
        await self._session.commit()
        await self._session.refresh(node)
        return {
            "id": node.id,
            "name": node.name,
            "kind": node.kind,
            "host": node.host,
            "enabled": node.enabled,
            "created": True,
        }

    async def insert_snapshot(
        self,
        pbx_node_id: int,
        taken_at: datetime,
        status: str,
        occupancy_pct: Decimal | float | None,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        occ = Decimal(str(occupancy_pct)) if occupancy_pct is not None else None
        snap = HealthSnapshot(
            pbx_node_id=pbx_node_id,
            taken_at=taken_at,
            status=status,
            occupancy_pct=occ,
            details=details,
        )
        self._session.add(snap)
        await self._session.commit()
        await self._session.refresh(snap)
        return {
            "id": snap.id,
            "pbx_node_id": snap.pbx_node_id,
            "taken_at": _iso(snap.taken_at),
            "status": snap.status,
            "occupancy_pct": _dec(snap.occupancy_pct),
            "details": snap.details,
        }

    async def insert_alarm(
        self,
        pbx_node_id: int,
        raised_at: datetime,
        severity: str,
        code: str | None,
        resource: str | None,
        message: str,
        raw: str | None,
    ) -> dict[str, Any] | None:
        stmt = select(Alarm).where(
            Alarm.pbx_node_id == pbx_node_id,
            Alarm.code == code,
            Alarm.resource == resource,
            Alarm.message == message,
            Alarm.cleared_at.is_(None),
        )
        existing = (await self._session.execute(stmt)).scalar_one_or_none()
        if existing is not None:
            return None
        alarm = Alarm(
            pbx_node_id=pbx_node_id,
            raised_at=raised_at,
            severity=severity,
            code=code,
            resource=resource,
            message=message,
            raw=raw,
        )
        self._session.add(alarm)
        await self._session.commit()
        await self._session.refresh(alarm)
        return _alarm_out(
            {
                "id": alarm.id,
                "pbx_node_id": alarm.pbx_node_id,
                "raised_at": alarm.raised_at,
                "cleared_at": alarm.cleared_at,
                "severity": alarm.severity,
                "code": alarm.code,
                "resource": alarm.resource,
                "message": alarm.message,
                "raw": alarm.raw,
            }
        )

    async def list_nodes(self) -> list[dict[str, Any]]:
        nodes = (await self._session.execute(select(PbxNode).order_by(PbxNode.id))).scalars().all()
        items: list[dict[str, Any]] = []
        for node in nodes:
            snap = (
                await self._session.execute(
                    select(HealthSnapshot)
                    .where(HealthSnapshot.pbx_node_id == node.id)
                    .order_by(HealthSnapshot.taken_at.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()
            open_count = (
                (
                    await self._session.execute(
                        select(Alarm).where(
                            Alarm.pbx_node_id == node.id, Alarm.cleared_at.is_(None)
                        )
                    )
                )
                .scalars()
                .all()
            )
            items.append(
                _node_out(
                    {
                        "id": node.id,
                        "name": node.name,
                        "kind": node.kind,
                        "host": node.host,
                        "enabled": node.enabled,
                    },
                    status=snap.status if snap else "unknown",
                    occupancy_pct=_dec(snap.occupancy_pct) if snap else None,
                    open_alarms=len(open_count),
                    taken_at=_iso(snap.taken_at) if snap else None,
                )
            )
        return items

    async def get_node_health(self, node_id: int) -> dict[str, Any] | None:
        node = await self._session.get(PbxNode, node_id)
        if node is None:
            return None
        snap = (
            await self._session.execute(
                select(HealthSnapshot)
                .where(HealthSnapshot.pbx_node_id == node.id)
                .order_by(HealthSnapshot.taken_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        alarms = (
            (
                await self._session.execute(
                    select(Alarm)
                    .where(Alarm.pbx_node_id == node.id, Alarm.cleared_at.is_(None))
                    .order_by(Alarm.raised_at.desc())
                )
            )
            .scalars()
            .all()
        )
        snapshot = None
        if snap is not None:
            snapshot = {
                "id": snap.id,
                "taken_at": _iso(snap.taken_at),
                "status": snap.status,
                "occupancy_pct": _dec(snap.occupancy_pct),
                "details": snap.details,
            }
        return {
            "node": {
                "id": node.id,
                "name": node.name,
                "kind": node.kind,
                "host": node.host,
                "enabled": node.enabled,
                "extra": node.extra,
            },
            "snapshot": snapshot,
            "alarms": [
                _alarm_out(
                    {
                        "id": a.id,
                        "pbx_node_id": a.pbx_node_id,
                        "raised_at": a.raised_at,
                        "cleared_at": a.cleared_at,
                        "severity": a.severity,
                        "code": a.code,
                        "resource": a.resource,
                        "message": a.message,
                        "raw": a.raw,
                    }
                )
                for a in alarms
            ],
        }

    async def list_alarms(self, **filters: Any) -> list[dict[str, Any]]:
        stmt = select(Alarm)
        if filters.get("severity"):
            stmt = stmt.where(Alarm.severity == filters["severity"])
        if filters.get("open") is True:
            stmt = stmt.where(Alarm.cleared_at.is_(None))
        if filters.get("from"):
            stmt = stmt.where(Alarm.raised_at >= filters["from"])
        if filters.get("to"):
            stmt = stmt.where(Alarm.raised_at <= filters["to"])
        rows = (await self._session.execute(stmt.order_by(Alarm.raised_at.desc()))).scalars().all()
        return [
            _alarm_out(
                {
                    "id": a.id,
                    "pbx_node_id": a.pbx_node_id,
                    "raised_at": a.raised_at,
                    "cleared_at": a.cleared_at,
                    "severity": a.severity,
                    "code": a.code,
                    "resource": a.resource,
                    "message": a.message,
                    "raw": a.raw,
                }
            )
            for a in rows
        ]


class InMemoryHealthRepository:
    """Для pytest без PostgreSQL."""

    def __init__(self) -> None:
        self._nodes: list[dict[str, Any]] = []
        self._snapshots: list[dict[str, Any]] = []
        self._alarms: list[dict[str, Any]] = []
        self._seq_node = 1
        self._seq_snap = 1
        self._seq_alarm = 1

    async def upsert_node(
        self, name: str, kind: str, host: str | None, extra: dict[str, Any]
    ) -> dict[str, Any]:
        for node in self._nodes:
            if node["name"] == name:
                node["kind"] = kind
                node["host"] = host
                node["extra"] = extra
                node["enabled"] = True
                return {**node, "created": False}
        node = {
            "id": self._seq_node,
            "name": name,
            "kind": kind,
            "host": host,
            "enabled": True,
            "extra": extra,
        }
        self._seq_node += 1
        self._nodes.append(node)
        return {**node, "created": True}

    async def insert_snapshot(
        self,
        pbx_node_id: int,
        taken_at: datetime,
        status: str,
        occupancy_pct: Decimal | float | None,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        snap = {
            "id": self._seq_snap,
            "pbx_node_id": pbx_node_id,
            "taken_at": taken_at,
            "status": status,
            "occupancy_pct": _dec(occupancy_pct)
            if not isinstance(occupancy_pct, float)
            else occupancy_pct,
            "details": details,
        }
        self._seq_snap += 1
        self._snapshots.append(snap)
        return {
            "id": snap["id"],
            "pbx_node_id": pbx_node_id,
            "taken_at": _iso(taken_at),
            "status": status,
            "occupancy_pct": snap["occupancy_pct"],
            "details": details,
        }

    async def insert_alarm(
        self,
        pbx_node_id: int,
        raised_at: datetime,
        severity: str,
        code: str | None,
        resource: str | None,
        message: str,
        raw: str | None,
    ) -> dict[str, Any] | None:
        for row in self._alarms:
            if (
                row["pbx_node_id"] == pbx_node_id
                and row.get("code") == code
                and row.get("resource") == resource
                and row["message"] == message
                and row.get("cleared_at") is None
            ):
                return None
        alarm = {
            "id": self._seq_alarm,
            "pbx_node_id": pbx_node_id,
            "raised_at": raised_at,
            "cleared_at": None,
            "severity": severity,
            "code": code,
            "resource": resource,
            "message": message,
            "raw": raw,
        }
        self._seq_alarm += 1
        self._alarms.append(alarm)
        return _alarm_out(alarm)

    def _latest_snap(self, node_id: int) -> dict[str, Any] | None:
        matches = [s for s in self._snapshots if s["pbx_node_id"] == node_id]
        if not matches:
            return None
        matches.sort(key=lambda s: s["taken_at"], reverse=True)
        return matches[0]

    def _open_alarms(self, node_id: int) -> list[dict[str, Any]]:
        return [
            a for a in self._alarms if a["pbx_node_id"] == node_id and a.get("cleared_at") is None
        ]

    async def list_nodes(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for node in self._nodes:
            snap = self._latest_snap(node["id"])
            items.append(
                _node_out(
                    node,
                    status=snap["status"] if snap else "unknown",
                    occupancy_pct=snap["occupancy_pct"] if snap else None,
                    open_alarms=len(self._open_alarms(node["id"])),
                    taken_at=_iso(snap["taken_at"]) if snap else None,
                )
            )
        return items

    async def get_node_health(self, node_id: int) -> dict[str, Any] | None:
        node = next((n for n in self._nodes if n["id"] == node_id), None)
        if node is None:
            return None
        snap = self._latest_snap(node_id)
        snapshot = None
        if snap is not None:
            snapshot = {
                "id": snap["id"],
                "taken_at": _iso(snap["taken_at"])
                if isinstance(snap["taken_at"], datetime)
                else snap["taken_at"],
                "status": snap["status"],
                "occupancy_pct": snap["occupancy_pct"],
                "details": snap["details"],
            }
        return {
            "node": {
                "id": node["id"],
                "name": node["name"],
                "kind": node["kind"],
                "host": node.get("host"),
                "enabled": node.get("enabled", True),
                "extra": node.get("extra") or {},
            },
            "snapshot": snapshot,
            "alarms": [_alarm_out(a) for a in self._open_alarms(node_id)],
        }

    async def list_alarms(self, **filters: Any) -> list[dict[str, Any]]:
        rows = list(self._alarms)
        if filters.get("severity"):
            rows = [a for a in rows if a["severity"] == filters["severity"]]
        if filters.get("open") is True:
            rows = [a for a in rows if a.get("cleared_at") is None]
        start = filters.get("from")
        end = filters.get("to")
        if start:
            rows = [a for a in rows if a["raised_at"] >= start]
        if end:
            rows = [a for a in rows if a["raised_at"] <= end]
        rows.sort(key=lambda a: a["raised_at"], reverse=True)
        return [_alarm_out(a) for a in rows]
