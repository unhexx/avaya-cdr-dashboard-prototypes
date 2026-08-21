"""Загрузка узлов и SAT/SNMP-фикстур в репозиторий здоровья."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.connectors.cm_snmp import CmSnmpConnector
from app.connectors.ipo_snmp import IpoSnmpConnector
from app.parsers.sat_health import parse_sat_bundle
from app.services.cdr_ingest import find_fixtures_root
from app.services.health_repo import HealthRepository

FIXTURE_TAKEN_AT = datetime(2026, 8, 21, 8, 0, tzinfo=UTC)

DEFAULT_NODES: tuple[dict[str, str], ...] = (
    {"name": "cm-lab", "kind": "cm", "host": "fixture-cm"},
    {"name": "ipo-lab", "kind": "ipo", "host": "fixture-ipo"},
    {"name": "sm-lab", "kind": "session_manager", "host": "fixture-sm"},
    {"name": "sbce-lab", "kind": "sbce", "host": "fixture-sbce"},
)


def _sat_dir(root: Path | None = None) -> Path:
    base = root or find_fixtures_root()
    return base / "cm" / "sat"


async def ingest_health_fixtures(
    repo: HealthRepository,
    root: Path | None = None,
) -> dict[str, int]:
    nodes_created = 0
    snapshots = 0
    alarms_inserted = 0

    node_ids: dict[str, int] = {}
    for spec in DEFAULT_NODES:
        row = await repo.upsert_node(
            name=spec["name"],
            kind=spec["kind"],
            host=spec["host"],
            extra={"source": "fixture"},
        )
        node_ids[spec["name"]] = int(row["id"])
        if row.get("created"):
            nodes_created += 1

    sat = _sat_dir(root)
    health_text = (
        (sat / "status_health.txt").read_text(encoding="utf-8")
        if (sat / "status_health.txt").is_file()
        else ""
    )
    alarms_text = (
        (sat / "display_alarms.txt").read_text(encoding="utf-8")
        if (sat / "display_alarms.txt").is_file()
        else ""
    )
    ds1_texts: list[str] = []
    ds1_path = sat / "status_ds1.txt"
    if ds1_path.is_file():
        ds1_texts.append(ds1_path.read_text(encoding="utf-8"))

    bundle = parse_sat_bundle(health_text, alarms_text, ds1_texts)
    cm_id = node_ids["cm-lab"]
    health = bundle.health
    occupancy = float(health.occupancy_pct) if health.occupancy_pct is not None else None
    cm_snmp = await CmSnmpConnector().poll_health()
    details: dict[str, Any] = {
        "source": "sat_fixture",
        "idle_cpu_pct": float(health.idle_cpu_pct) if health.idle_cpu_pct is not None else None,
        "system_management": health.system_management,
        "last_reload": health.last_reload,
        "alarms_major": health.alarms_major,
        "alarms_minor": health.alarms_minor,
        "alarms_warning": health.alarms_warning,
        "ds1": [row.as_details() for row in bundle.ds1],
        "connector": "mock",
        "snmp_mock": {
            "status": cm_snmp.get("status"),
            "occupancy_pct": cm_snmp.get("occupancy_pct"),
            "oids": cm_snmp.get("oids") or {},
        },
    }
    await repo.insert_snapshot(
        pbx_node_id=cm_id,
        taken_at=FIXTURE_TAKEN_AT,
        status=health.status,
        occupancy_pct=occupancy,
        details=details,
    )
    snapshots += 1
    for alarm in bundle.alarms:
        inserted = await repo.insert_alarm(
            pbx_node_id=cm_id,
            raised_at=FIXTURE_TAKEN_AT,
            severity=alarm.severity,
            code=alarm.code,
            resource=alarm.resource,
            message=alarm.message,
            raw=alarm.raw,
        )
        if inserted is not None:
            alarms_inserted += 1

    ipo_poll = await IpoSnmpConnector().poll_health()
    await repo.insert_snapshot(
        pbx_node_id=node_ids["ipo-lab"],
        taken_at=FIXTURE_TAKEN_AT,
        status=str(ipo_poll.get("status") or "ok"),
        occupancy_pct=ipo_poll.get("occupancy_pct"),
        details={
            "source": "snmp_mock",
            "connector": "ipo_snmp",
            "oids": ipo_poll.get("oids") or {},
        },
    )
    snapshots += 1

    for idle_name in ("sm-lab", "sbce-lab"):
        await repo.insert_snapshot(
            pbx_node_id=node_ids[idle_name],
            taken_at=FIXTURE_TAKEN_AT,
            status="unknown",
            occupancy_pct=None,
            details={"source": "idle", "reason": "no_live_host"},
        )
        snapshots += 1

    return {
        "nodes": nodes_created,
        "snapshots": snapshots,
        "alarms": alarms_inserted,
    }
