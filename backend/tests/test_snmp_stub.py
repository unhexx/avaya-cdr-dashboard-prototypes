"""SNMP-заглушки: mock OID без живого опроса и без pysnmp."""

from pathlib import Path

import pytest

from app.config import get_settings
from app.connectors.cm_snmp import MOCK_OIDS as CM_OIDS
from app.connectors.cm_snmp import CmSnmpConnector
from app.connectors.factory import build_connectors
from app.connectors.ipo_snmp import IpoSnmpConnector
from app.parsers.sat_health import is_sat_allowed


@pytest.mark.asyncio
async def test_cm_snmp_fixture_occupancy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_FIXTURES", "true")
    monkeypatch.setenv("ENABLE_LIVE_CONNECTORS", "false")
    get_settings.cache_clear()
    payload = await CmSnmpConnector().poll_health()
    assert payload["status"] == "ok"
    assert payload["source"] == "mock_oid"
    assert payload["occupancy_pct"] == float(CM_OIDS["mock.cm.occupancyPct"])


@pytest.mark.asyncio
async def test_ipo_snmp_fixture_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_FIXTURES", "true")
    monkeypatch.setenv("ENABLE_LIVE_CONNECTORS", "false")
    get_settings.cache_clear()
    payload = await IpoSnmpConnector().poll_health()
    assert payload["connector"] == "ipo_snmp"
    assert payload["occupancy_pct"] == 8.5


@pytest.mark.asyncio
async def test_live_snmp_skipped_when_enabled_without_stack(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("USE_FIXTURES", "false")
    monkeypatch.setenv("ENABLE_LIVE_CONNECTORS", "true")
    monkeypatch.setenv("CM_SNMP_HOST", "192.0.2.10")
    get_settings.cache_clear()
    payload = await CmSnmpConnector().poll_health()
    assert payload["status"] == "skipped"
    assert payload["reason"] == "live_snmp_not_in_v1"


def test_no_pysnmp_or_sysmonitor_in_connectors() -> None:
    root = Path(__file__).resolve().parents[1] / "app" / "connectors"
    for path in root.glob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        assert "pysnmp" not in text
        assert "easysnmp" not in text
        if "sysmonitor" in text:
            assert "не реализуется" in text or "запрещ" in text


def test_factory_has_health_connectors_not_sysmonitor() -> None:
    names = [c.name for c in build_connectors()]
    assert "mock" in names
    assert "cm_sat" in names
    assert "cm_snmp" in names
    assert "ipo_snmp" in names
    assert all("sysmonitor" not in n for n in names)
    assert is_sat_allowed("display alarms")
