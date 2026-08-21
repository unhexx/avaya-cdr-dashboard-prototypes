"""Загрузка фикстур ARS/IPO и longest-prefix поиск по dialplan_entries."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dialplan import DialplanEntry
from app.parsers.dialplan_ars import ArsRow, parse_list_ars_analysis
from app.parsers.dialplan_ipo import IpoShortcodeRow, parse_ipo_shortcodes_csv
from app.services.cdr_ingest import find_fixtures_root

FIXTURE_SYNCED_AT = datetime(2026, 8, 21, 8, 0, tzinfo=UTC)


def _row_out(entry: dict[str, Any]) -> dict[str, Any]:
    synced = entry.get("synced_at")
    if isinstance(synced, datetime):
        synced = synced.isoformat()
    return {
        "id": entry["id"],
        "source": entry["source"],
        "match_prefix": entry["match_prefix"],
        "min_digits": entry.get("min_digits"),
        "max_digits": entry.get("max_digits"),
        "route": entry.get("route"),
        "call_type": entry.get("call_type"),
        "node_number": entry.get("node_number"),
        "location": entry.get("location"),
        "raw": entry.get("raw"),
        "synced_at": synced,
    }


def load_fixture_dialplan(root: Path | None = None) -> list[dict[str, Any]]:
    """ARS + IPO shortcodes из docs/fixtures → словари под DialplanEntry."""
    base = root or find_fixtures_root()
    rows: list[dict[str, Any]] = []

    ars_path = base / "cm" / "sat" / "list_ars_analysis.txt"
    if ars_path.is_file():
        for item in parse_list_ars_analysis(ars_path.read_text(encoding="utf-8")):
            rows.append(_ars_to_dict(item))

    ipo_path = base / "smdr" / "ipo-shortcodes.csv"
    if ipo_path.is_file():
        for item in parse_ipo_shortcodes_csv(ipo_path.read_text(encoding="utf-8")):
            rows.append(_ipo_to_dict(item))

    return rows


def _ars_to_dict(item: ArsRow) -> dict[str, Any]:
    return {
        "source": "ars",
        "match_prefix": item.match_prefix,
        "min_digits": item.min_digits,
        "max_digits": item.max_digits,
        "route": item.route,
        "call_type": item.call_type,
        "node_number": item.node_number,
        "location": item.location,
        "raw": item.raw,
        "synced_at": FIXTURE_SYNCED_AT,
    }


def _ipo_to_dict(item: IpoShortcodeRow) -> dict[str, Any]:
    route = item.feature
    if item.line_group:
        route = f"{item.feature}:{item.line_group}" if item.feature else item.line_group
    return {
        "source": "ipo_shortcode",
        "match_prefix": item.match_prefix,
        "min_digits": None,
        "max_digits": None,
        "route": route,
        "call_type": item.feature,
        "node_number": item.telephone_number,
        "location": None,
        "raw": item.raw,
        "synced_at": FIXTURE_SYNCED_AT,
    }


def longest_prefix_match(
    entries: list[dict[str, Any]],
    q: str,
    source: str | None = None,
) -> list[dict[str, Any]]:
    """
    Фильтр по source, затем строки, чей match_prefix — префикс q.
    Пустой q — все (с учётом source). Сортировка: длина префикса ↓, затем prefix.
    """
    needle = (q or "").strip()
    filtered: list[dict[str, Any]] = []
    for entry in entries:
        if source and entry.get("source") != source:
            continue
        prefix = entry.get("match_prefix") or ""
        if not needle or needle.startswith(prefix):
            filtered.append(entry)
    filtered.sort(key=lambda e: (-len(e.get("match_prefix") or ""), e.get("match_prefix") or ""))
    return filtered


class DialplanRepository(Protocol):
    async def replace_all(self, rows: list[dict[str, Any]]) -> dict[str, int]: ...

    async def list_entries(
        self, q: str = "", source: str | None = None
    ) -> list[dict[str, Any]]: ...


class SqlDialplanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def replace_all(self, rows: list[dict[str, Any]]) -> dict[str, int]:
        await self._session.execute(delete(DialplanEntry))
        inserted = 0
        for row in rows:
            self._session.add(DialplanEntry(**{k: v for k, v in row.items() if k != "id"}))
            inserted += 1
        await self._session.commit()
        return {"inserted": inserted, "total": inserted}

    async def list_entries(
        self, q: str = "", source: str | None = None
    ) -> list[dict[str, Any]]:
        stmt = select(DialplanEntry)
        if source:
            stmt = stmt.where(DialplanEntry.source == source)
        result = await self._session.execute(stmt)
        items = [
            {
                "id": obj.id,
                "source": obj.source,
                "match_prefix": obj.match_prefix,
                "min_digits": obj.min_digits,
                "max_digits": obj.max_digits,
                "route": obj.route,
                "call_type": obj.call_type,
                "node_number": obj.node_number,
                "location": obj.location,
                "raw": obj.raw,
                "synced_at": obj.synced_at,
            }
            for obj in result.scalars().all()
        ]
        return [_row_out(e) for e in longest_prefix_match(items, q, source=None)]


class InMemoryDialplanRepository:
    """In-memory для pytest без PostgreSQL."""

    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = []
        self._next_id = 1

    async def replace_all(self, rows: list[dict[str, Any]]) -> dict[str, int]:
        self._items = []
        self._next_id = 1
        for row in rows:
            payload = dict(row)
            payload["id"] = self._next_id
            self._next_id += 1
            self._items.append(payload)
        return {"inserted": len(self._items), "total": len(self._items)}

    async def list_entries(
        self, q: str = "", source: str | None = None
    ) -> list[dict[str, Any]]:
        matched = longest_prefix_match(self._items, q, source=source)
        return [_row_out(e) for e in matched]


async def sync_dialplan_fixtures(
    repo: DialplanRepository, root: Path | None = None
) -> dict[str, int]:
    rows = load_fixture_dialplan(root)
    stats = await repo.replace_all(rows)
    stats["parsed"] = len(rows)
    by_source: dict[str, int] = {}
    for row in rows:
        by_source[row["source"]] = by_source.get(row["source"], 0) + 1
    stats["by_source"] = by_source  # type: ignore[assignment]
    return stats
