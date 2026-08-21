"""Mock-коннектор: здоровье из SAT-фикстур, без живых хостов."""

from typing import Any

from app.parsers.sat_health import parse_sat_bundle
from app.services.cdr_ingest import find_fixtures_root


class MockConnector:
    name = "mock"

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def poll_health(self) -> dict[str, Any]:
        root = find_fixtures_root() / "cm" / "sat"
        health_path = root / "status_health.txt"
        alarms_path = root / "display_alarms.txt"
        ds1_path = root / "status_ds1.txt"
        if not health_path.is_file():
            return {"status": "unknown", "connector": self.name, "reason": "no_sat_fixtures"}
        bundle = parse_sat_bundle(
            health_path.read_text(encoding="utf-8"),
            alarms_path.read_text(encoding="utf-8") if alarms_path.is_file() else "",
            [ds1_path.read_text(encoding="utf-8")] if ds1_path.is_file() else [],
        )
        health = bundle.health
        occupancy = float(health.occupancy_pct) if health.occupancy_pct is not None else None
        return {
            "status": health.status,
            "connector": self.name,
            "source": "sat_fixture",
            "occupancy_pct": occupancy,
            "idle_cpu_pct": float(health.idle_cpu_pct) if health.idle_cpu_pct is not None else None,
            "alarms_open": len(bundle.alarms),
            "ds1": [row.as_details() for row in bundle.ds1],
        }

    async def ingest_once(self) -> list[dict[str, Any]]:
        return []
