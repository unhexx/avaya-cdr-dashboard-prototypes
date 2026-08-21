"""API CDR на in-memory репозитории (без живой АТС и без PostgreSQL)."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.cdr import get_cdr_repo
from app.api.pbx import get_health_repo
from app.main import create_app
from app.services.cdr_ingest import generate_mock_cdrs, load_fixture_cdrs
from app.services.cdr_repo import InMemoryCdrRepository
from app.services.health_repo import InMemoryHealthRepository


@pytest.fixture
def api() -> Iterator[tuple[TestClient, InMemoryCdrRepository]]:
    repo = InMemoryCdrRepository()
    health = InMemoryHealthRepository()
    application = create_app()

    async def _override() -> InMemoryCdrRepository:
        return repo

    async def _health() -> InMemoryHealthRepository:
        return health

    application.dependency_overrides[get_cdr_repo] = _override
    application.dependency_overrides[get_health_repo] = _health
    with TestClient(application) as client:
        yield client, repo


def test_ingest_fixtures_and_list(api: tuple[TestClient, InMemoryCdrRepository]) -> None:
    client, _repo = api
    response = client.post("/api/ingest/fixtures")
    assert response.status_code == 200
    body = response.json()
    assert body["inserted"] > 0
    listed = client.get("/api/cdr", params={"page_size": 50})
    assert listed.status_code == 200
    payload = listed.json()
    assert payload["total"] == body["inserted"]
    assert payload["items"]
    assert "raw_record" not in payload["items"][0]


def test_detail_includes_raw_and_dedup(
    api: tuple[TestClient, InMemoryCdrRepository],
) -> None:
    client, repo = api
    rows = load_fixture_cdrs()
    first = client.post("/api/ingest/fixtures").json()
    second = client.post("/api/ingest/fixtures").json()
    assert second["inserted"] == 0
    assert second["skipped"] == first["inserted"]
    detail = client.get(f"/api/cdr/{repo._items[0]['id']}")
    assert detail.status_code == 200
    assert detail.json()["raw_record"]
    assert len(detail.json()["raw_hash"]) == 64
    assert rows


def test_filter_and_export_csv(api: tuple[TestClient, InMemoryCdrRepository]) -> None:
    client, _repo = api
    client.post("/api/ingest/fixtures")
    inbound = client.get("/api/cdr", params={"direction": "inbound"})
    assert inbound.status_code == 200
    assert inbound.json()["total"] >= 1
    q = client.get("/api/cdr", params={"q": "79031234567"})
    assert q.json()["total"] >= 1
    export = client.get("/api/export", params={"format": "csv"})
    assert export.status_code == 200
    assert "text/csv" in export.headers["content-type"]
    assert "calling_number" in export.text
    js = client.get("/api/export", params={"format": "json"})
    assert js.status_code == 200
    assert js.json()


def test_mock_generate(api: tuple[TestClient, InMemoryCdrRepository]) -> None:
    client, _repo = api
    response = client.post("/api/mock-generate", params={"n": 20})
    assert response.json()["inserted"] == 20
    assert generate_mock_cdrs(3)
