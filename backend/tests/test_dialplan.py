"""Парсеры ARS/IPO и API /api/dialplan (in-memory, без PostgreSQL)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.cdr import get_cdr_repo
from app.api.dialplan import get_dialplan_repo
from app.api.pbx import get_health_repo
from app.main import create_app
from app.parsers.dialplan_ars import parse_list_ars_analysis
from app.parsers.dialplan_ipo import parse_ipo_shortcodes_csv
from app.services.cdr_repo import InMemoryCdrRepository
from app.services.dialplan import (
    InMemoryDialplanRepository,
    load_fixture_dialplan,
    longest_prefix_match,
)
from app.services.health_repo import InMemoryHealthRepository

FIXTURES = Path(__file__).resolve().parents[2] / "docs" / "fixtures"


@pytest.fixture
def api() -> Iterator[tuple[TestClient, InMemoryDialplanRepository]]:
    dialplan = InMemoryDialplanRepository()
    cdr = InMemoryCdrRepository()
    health = InMemoryHealthRepository()
    application = create_app()

    async def _dialplan() -> InMemoryDialplanRepository:
        return dialplan

    async def _cdr() -> InMemoryCdrRepository:
        return cdr

    async def _health() -> InMemoryHealthRepository:
        return health

    application.dependency_overrides[get_dialplan_repo] = _dialplan
    application.dependency_overrides[get_cdr_repo] = _cdr
    application.dependency_overrides[get_health_repo] = _health
    with TestClient(application) as client:
        yield client, dialplan


def test_parse_list_ars_analysis() -> None:
    text = (FIXTURES / "cm" / "sat" / "list_ars_analysis.txt").read_text(encoding="utf-8")
    rows = parse_list_ars_analysis(text)
    assert len(rows) == 6
    by_prefix = {r.match_prefix: r for r in rows}
    assert by_prefix["810"].min_digits == 11
    assert by_prefix["810"].max_digits == 11
    assert by_prefix["810"].route == "5"
    assert by_prefix["810"].call_type == "intl"
    assert by_prefix["810"].location == "1"
    assert by_prefix["8"].call_type == "hnpa"
    assert by_prefix["300"].call_type == "vdn"


def test_parse_ipo_shortcodes() -> None:
    text = (FIXTURES / "smdr" / "ipo-shortcodes.csv").read_text(encoding="utf-8")
    rows = parse_ipo_shortcodes_csv(text)
    assert len(rows) == 5
    by_prefix = {r.match_prefix: r for r in rows}
    assert "9" in by_prefix
    assert by_prefix["9"].feature == "Dial"
    assert by_prefix["9"].line_group == "7"
    assert by_prefix["12"].feature == "DialExtn"
    assert by_prefix["*17"].feature == "CallPickupAny"
    assert by_prefix["3001"].telephone_number == "3001"


def test_longest_prefix_order() -> None:
    entries = [
        {"id": 1, "source": "ars", "match_prefix": "8"},
        {"id": 2, "source": "ars", "match_prefix": "810"},
        {"id": 3, "source": "ars", "match_prefix": "9"},
        {"id": 4, "source": "ipo_shortcode", "match_prefix": "81"},
    ]
    matched = longest_prefix_match(entries, "81012345678")
    prefixes = [e["match_prefix"] for e in matched]
    assert prefixes[0] == "810"
    assert "8" in prefixes
    assert "81" in prefixes
    assert "9" not in prefixes


def test_load_fixtures_combined() -> None:
    rows = load_fixture_dialplan(FIXTURES)
    sources = {r["source"] for r in rows}
    assert "ars" in sources
    assert "ipo_shortcode" in sources
    assert len(rows) >= 11


def test_sync_and_search_api(api: tuple[TestClient, InMemoryDialplanRepository]) -> None:
    client, _repo = api
    empty = client.get("/api/dialplan")
    assert empty.status_code == 200
    assert empty.json()["total"] == 0

    sync = client.post("/api/dialplan/sync")
    assert sync.status_code == 200
    body = sync.json()
    assert body["inserted"] >= 11
    assert body["parsed"] == body["inserted"]
    assert body["by_source"]["ars"] == 6
    assert body["by_source"]["ipo_shortcode"] == 5

    all_rows = client.get("/api/dialplan")
    assert all_rows.json()["total"] == body["inserted"]

    intl = client.get("/api/dialplan", params={"q": "8105551212"})
    payload = intl.json()
    assert payload["total"] >= 1
    assert payload["items"][0]["match_prefix"] == "810"
    assert payload["items"][0]["call_type"] == "intl"

    ars_only = client.get("/api/dialplan", params={"source": "ars"})
    assert ars_only.json()["total"] == 6

    ipo = client.get("/api/dialplan", params={"q": "912345", "source": "ipo_shortcode"})
    assert ipo.json()["total"] >= 1
    assert ipo.json()["items"][0]["match_prefix"] == "9"
