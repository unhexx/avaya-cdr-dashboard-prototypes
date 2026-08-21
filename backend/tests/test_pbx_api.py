"""API узлов АТС и аварий на in-memory репозитории (без живой АТС)."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.cdr import get_cdr_repo
from app.api.pbx import get_health_repo
from app.main import create_app
from app.services.cdr_repo import InMemoryCdrRepository
from app.services.health_repo import InMemoryHealthRepository


@pytest.fixture
def api() -> Iterator[tuple[TestClient, InMemoryHealthRepository]]:
    cdr = InMemoryCdrRepository()
    health = InMemoryHealthRepository()
    application = create_app()

    async def _cdr() -> InMemoryCdrRepository:
        return cdr

    async def _health() -> InMemoryHealthRepository:
        return health

    application.dependency_overrides[get_cdr_repo] = _cdr
    application.dependency_overrides[get_health_repo] = _health
    with TestClient(application) as client:
        yield client, health


def test_pbx_empty_before_ingest(api: tuple[TestClient, InMemoryHealthRepository]) -> None:
    client, _repo = api
    response = client.get("/api/pbx")
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_ingest_sat_and_list_nodes(api: tuple[TestClient, InMemoryHealthRepository]) -> None:
    client, _repo = api
    ingested = client.post("/api/ingest/fixtures")
    assert ingested.status_code == 200
    body = ingested.json()
    assert body["nodes"] == 4
    assert body["snapshots"] >= 4
    assert body["alarms"] == 2
    listed = client.get("/api/pbx")
    assert listed.status_code == 200
    items = listed.json()["items"]
    names = {n["name"] for n in items}
    assert names == {"cm-lab", "ipo-lab", "sm-lab", "sbce-lab"}
    cm = next(n for n in items if n["name"] == "cm-lab")
    assert cm["kind"] == "cm"
    assert cm["status"] == "degraded"
    assert cm["occupancy_pct"] == 12.0
    assert cm["open_alarms"] == 2
    ipo = next(n for n in items if n["name"] == "ipo-lab")
    assert ipo["status"] == "ok"
    assert ipo["occupancy_pct"] == 8.5


def test_node_health_detail_and_404(api: tuple[TestClient, InMemoryHealthRepository]) -> None:
    client, _repo = api
    client.post("/api/ingest/fixtures")
    nodes = client.get("/api/pbx").json()["items"]
    cm_id = next(n["id"] for n in nodes if n["name"] == "cm-lab")
    detail = client.get(f"/api/pbx/{cm_id}/health")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["node"]["name"] == "cm-lab"
    assert payload["snapshot"]["status"] == "degraded"
    assert payload["snapshot"]["details"]["source"] == "sat_fixture"
    assert payload["snapshot"]["details"]["ds1"][0]["location"] == "01A0517"
    assert len(payload["alarms"]) == 2
    missing = client.get("/api/pbx/9999/health")
    assert missing.status_code == 404


def test_alarms_open_filter_and_dedup(api: tuple[TestClient, InMemoryHealthRepository]) -> None:
    client, _repo = api
    first = client.post("/api/ingest/fixtures").json()
    second = client.post("/api/ingest/fixtures").json()
    assert first["alarms"] == 2
    assert second["alarms"] == 0
    open_alarms = client.get("/api/alarms", params={"open": "true"})
    assert open_alarms.status_code == 200
    assert open_alarms.json()["total"] == 2
    warning = client.get("/api/alarms", params={"severity": "warning", "open": "true"})
    assert warning.json()["total"] == 1
    minor = client.get("/api/alarms", params={"severity": "minor"})
    assert minor.json()["total"] == 1


def test_openapi_documents_pbx_routes() -> None:
    client = TestClient(create_app())
    spec = client.get("/api/openapi.json").json()
    paths = spec["paths"]
    assert "/api/pbx" in paths
    assert "/api/pbx/{node_id}/health" in paths
    assert "/api/alarms" in paths
