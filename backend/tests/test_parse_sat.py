"""Золотые фикстуры SAT: status health, display alarms, status ds1."""

from pathlib import Path

from app.parsers.sat_health import (
    is_sat_allowed,
    parse_display_alarms,
    parse_sat_bundle,
    parse_status_ds1,
    parse_status_health,
)

SAT = Path(__file__).resolve().parents[2] / "docs" / "fixtures" / "cm" / "sat"


def _read(name: str) -> str:
    return (SAT / name).read_text(encoding="utf-8")


def test_sat_allowlist_read_only() -> None:
    assert is_sat_allowed("status health")
    assert is_sat_allowed("status ds1 01A0517")
    assert is_sat_allowed("list ars analysis")
    assert not is_sat_allowed("change system-parameters cdr")
    assert not is_sat_allowed("busyout trunk 1")
    assert not is_sat_allowed("add station 1234")
    assert not is_sat_allowed("")


def test_status_health_occupancy_and_degraded() -> None:
    parsed = parse_status_health(_read("status_health.txt"))
    assert parsed.occupancy_pct is not None
    assert float(parsed.occupancy_pct) == 12.0
    assert parsed.idle_cpu_pct is not None
    assert float(parsed.idle_cpu_pct) == 84.0
    assert parsed.system_management == "up"
    assert parsed.alarms_major == 0
    assert parsed.alarms_minor == 1
    assert parsed.alarms_warning == 2
    assert parsed.status == "degraded"


def test_display_alarms_two_open() -> None:
    rows = parse_display_alarms(_read("display_alarms.txt"))
    assert len(rows) == 2
    ds1 = rows[0]
    assert ds1.port == "01A0517"
    assert ds1.resource_type == "ds1"
    assert ds1.severity == "warning"
    assert "slip" in ds1.message
    medpro = rows[1]
    assert medpro.port == "MEDPRO"
    assert medpro.alt_name == "ip-board"
    assert medpro.severity == "minor"
    assert "high-occupancy" in medpro.message


def test_status_ds1_fields() -> None:
    ds1 = parse_status_ds1(_read("status_ds1.txt"))
    assert ds1.location == "01A0517"
    assert ds1.alarms == "none"
    assert ds1.slip_count == 0
    assert ds1.code == "hdb3"
    assert ds1.framing == "crc4"
    assert ds1.signaling == "isdn-pri"


def test_bundle_from_fixtures() -> None:
    bundle = parse_sat_bundle(
        _read("status_health.txt"),
        _read("display_alarms.txt"),
        [_read("status_ds1.txt")],
    )
    assert bundle.health.status == "degraded"
    assert len(bundle.alarms) == 2
    assert bundle.ds1[0].location == "01A0517"
