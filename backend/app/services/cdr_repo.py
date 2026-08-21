"""Репозиторий CDR: SQLAlchemy и in-memory (тесты без PostgreSQL)."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Protocol

from sqlalchemy import Select, func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cdr import CdrRecord
from app.parsers.common import sha256_raw
from app.parsers.types import NormalizedCdr

_PAGE_SIZES = {10, 25, 50, 100, 500}


def clamp_page_size(value: int) -> int:
    if value in _PAGE_SIZES:
        return value
    return min(max(value, 1), 500)


class CdrRepository(Protocol):
    async def insert_many(self, rows: list[NormalizedCdr]) -> dict[str, int]: ...

    async def list_page(self, **filters: Any) -> dict[str, Any]: ...

    async def get(self, cdr_id: int) -> dict[str, Any] | None: ...

    async def export_rows(self, **filters: Any) -> list[dict[str, Any]]: ...


def _row_to_values(row: NormalizedCdr) -> dict[str, Any]:
    payload = asdict(row)
    payload.pop("extra", None)
    payload["raw_hash"] = sha256_raw(row.raw_record)
    payload["end_time"] = None
    return payload


def _orm_to_dict(obj: CdrRecord, *, include_raw: bool) -> dict[str, Any]:
    data = {
        "id": obj.id,
        "ucid": obj.ucid,
        "call_id": obj.call_id,
        "start_time": obj.start_time.isoformat() if obj.start_time else None,
        "duration_seconds": obj.duration_seconds,
        "ring_duration_seconds": obj.ring_duration_seconds,
        "hold_duration_seconds": obj.hold_duration_seconds,
        "park_duration_seconds": obj.park_duration_seconds,
        "calling_number": obj.calling_number,
        "dialed_number": obj.dialed_number,
        "connected_number": obj.connected_number,
        "direction": obj.direction,
        "disposition": obj.disposition,
        "condition_code": obj.condition_code,
        "trunk_in": obj.trunk_in,
        "trunk_out": obj.trunk_out,
        "account_code": obj.account_code,
        "vdn": obj.vdn,
        "agent_extension": obj.agent_extension,
        "source_system": obj.source_system,
        "is_internal": obj.is_internal,
        "is_transferred": obj.is_transferred,
        "is_conferenced": obj.is_conferenced,
    }
    if include_raw:
        data["raw_record"] = obj.raw_record
        data["raw_hash"] = obj.raw_hash
    return data


class SqlCdrRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def insert_many(self, rows: list[NormalizedCdr]) -> dict[str, int]:
        inserted = 0
        skipped = 0
        for row in rows:
            values = _row_to_values(row)
            stmt = (
                insert(CdrRecord)
                .values(**values)
                .on_conflict_do_nothing(index_elements=["source_system", "raw_hash"])
            )
            result = await self._session.execute(stmt)
            rowcount = getattr(result, "rowcount", 0) or 0
            if rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        await self._session.commit()
        return {"inserted": inserted, "skipped": skipped, "total": len(rows)}

    def _filter_stmt(self, **filters: Any) -> Select[tuple[CdrRecord]]:
        stmt: Select[tuple[CdrRecord]] = select(CdrRecord)
        if filters.get("from"):
            stmt = stmt.where(CdrRecord.start_time >= filters["from"])
        if filters.get("to"):
            stmt = stmt.where(CdrRecord.start_time <= filters["to"])
        if filters.get("direction"):
            stmt = stmt.where(CdrRecord.direction == filters["direction"])
        if filters.get("disposition"):
            stmt = stmt.where(CdrRecord.disposition == filters["disposition"])
        match = filters.get("match") or "contains"
        for field_name, column in (
            ("calling_number", CdrRecord.calling_number),
            ("dialed_number", CdrRecord.dialed_number),
            ("agent_extension", CdrRecord.agent_extension),
            ("vdn", CdrRecord.vdn),
            ("account_code", CdrRecord.account_code),
        ):
            value = filters.get(field_name)
            if not value:
                continue
            if match == "exact":
                stmt = stmt.where(column == value)
            elif match == "prefix":
                stmt = stmt.where(column.startswith(value))
            else:
                stmt = stmt.where(column.contains(value))
        trunk = filters.get("trunk")
        if trunk:
            stmt = stmt.where(or_(CdrRecord.trunk_in == trunk, CdrRecord.trunk_out == trunk))
        q = filters.get("q")
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                or_(
                    CdrRecord.calling_number.ilike(like),
                    CdrRecord.dialed_number.ilike(like),
                    CdrRecord.ucid.ilike(like),
                    CdrRecord.connected_number.ilike(like),
                )
            )
        return stmt

    async def list_page(self, **filters: Any) -> dict[str, Any]:
        page = max(int(filters.get("page") or 1), 1)
        page_size = clamp_page_size(int(filters.get("page_size") or 25))
        sort = str(filters.get("sort") or "-start_time")
        desc = sort.startswith("-")
        key = sort.lstrip("-")
        column = getattr(CdrRecord, key, CdrRecord.start_time)
        order = column.desc() if desc else column.asc()
        base = self._filter_stmt(**filters)
        subq = base.subquery()
        total = int(
            (await self._session.execute(select(func.count()).select_from(subq))).scalar_one()
        )
        talk = (
            await self._session.execute(select(func.coalesce(func.sum(subq.c.duration_seconds), 0)))
        ).scalar_one()
        rows = (
            (
                await self._session.execute(
                    base.order_by(order).offset((page - 1) * page_size).limit(page_size)
                )
            )
            .scalars()
            .all()
        )
        return {
            "items": [_orm_to_dict(r, include_raw=False) for r in rows],
            "page": page,
            "page_size": page_size,
            "total": total,
            "summary": {"count": total, "talk_seconds": int(talk or 0)},
        }

    async def get(self, cdr_id: int) -> dict[str, Any] | None:
        obj = await self._session.get(CdrRecord, cdr_id)
        if obj is None:
            return None
        return _orm_to_dict(obj, include_raw=True)

    async def export_rows(self, **filters: Any) -> list[dict[str, Any]]:
        base = self._filter_stmt(**filters).order_by(CdrRecord.start_time.desc()).limit(10000)
        rows = (await self._session.execute(base)).scalars().all()
        return [_orm_to_dict(r, include_raw=True) for r in rows]


class InMemoryCdrRepository:
    """Для pytest: тот же контракт, без PostgreSQL."""

    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = []
        self._seq = 1

    async def insert_many(self, rows: list[NormalizedCdr]) -> dict[str, int]:
        hashes = {(i["source_system"], i.get("raw_hash")) for i in self._items}
        inserted = 0
        skipped = 0
        for row in rows:
            values = _row_to_values(row)
            key = (values["source_system"], values["raw_hash"])
            if key in hashes:
                skipped += 1
                continue
            values["id"] = self._seq
            self._seq += 1
            values["start_time"] = row.start_time
            hashes.add(key)
            self._items.append(values)
            inserted += 1
        return {"inserted": inserted, "skipped": skipped, "total": len(rows)}

    def _match(self, item: dict[str, Any], **filters: Any) -> bool:
        if filters.get("direction") and item.get("direction") != filters["direction"]:
            return False
        if filters.get("disposition") and item.get("disposition") != filters["disposition"]:
            return False
        match = filters.get("match") or "contains"
        for field_name in (
            "calling_number",
            "dialed_number",
            "agent_extension",
            "vdn",
            "account_code",
        ):
            needle = filters.get(field_name)
            hay = item.get(field_name) or ""
            if not needle:
                continue
            if match == "exact" and hay != needle:
                return False
            if match == "prefix" and not str(hay).startswith(str(needle)):
                return False
            if match == "contains" and str(needle) not in str(hay):
                return False
        q = filters.get("q")
        if q:
            blob = " ".join(
                str(item.get(k) or "")
                for k in ("calling_number", "dialed_number", "ucid", "connected_number")
            )
            if q not in blob:
                return False
        return True

    def _as_out(self, item: dict[str, Any], *, include_raw: bool) -> dict[str, Any]:
        start = item["start_time"]
        data = {
            "id": item["id"],
            "ucid": item.get("ucid"),
            "call_id": item.get("call_id"),
            "start_time": start.isoformat() if hasattr(start, "isoformat") else start,
            "duration_seconds": item.get("duration_seconds", 0),
            "ring_duration_seconds": item.get("ring_duration_seconds", 0),
            "calling_number": item.get("calling_number"),
            "dialed_number": item.get("dialed_number"),
            "direction": item.get("direction"),
            "disposition": item.get("disposition"),
            "condition_code": item.get("condition_code"),
            "trunk_in": item.get("trunk_in"),
            "trunk_out": item.get("trunk_out"),
            "account_code": item.get("account_code"),
            "vdn": item.get("vdn"),
            "agent_extension": item.get("agent_extension"),
            "source_system": item.get("source_system"),
            "is_internal": item.get("is_internal", False),
            "is_transferred": item.get("is_transferred", False),
            "is_conferenced": item.get("is_conferenced", False),
        }
        if include_raw:
            data["raw_record"] = item.get("raw_record")
            data["raw_hash"] = item.get("raw_hash")
        return data

    async def list_page(self, **filters: Any) -> dict[str, Any]:
        matched = [i for i in self._items if self._match(i, **filters)]
        page = max(int(filters.get("page") or 1), 1)
        page_size = clamp_page_size(int(filters.get("page_size") or 25))
        sort = str(filters.get("sort") or "-start_time")
        reverse = sort.startswith("-")
        key = sort.lstrip("-")
        matched.sort(key=lambda r: r.get(key) or 0, reverse=reverse)
        total = len(matched)
        talk = sum(int(i.get("duration_seconds") or 0) for i in matched)
        start = (page - 1) * page_size
        chunk = matched[start : start + page_size]
        return {
            "items": [self._as_out(i, include_raw=False) for i in chunk],
            "page": page,
            "page_size": page_size,
            "total": total,
            "summary": {"count": total, "talk_seconds": talk},
        }

    async def get(self, cdr_id: int) -> dict[str, Any] | None:
        for item in self._items:
            if item["id"] == cdr_id:
                return self._as_out(item, include_raw=True)
        return None

    async def export_rows(self, **filters: Any) -> list[dict[str, Any]]:
        matched = [i for i in self._items if self._match(i, **filters)]
        return [self._as_out(i, include_raw=True) for i in matched]
