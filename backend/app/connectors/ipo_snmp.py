"""SNMP v2c IP Office. Живой опрос пропускается; SysMonitor не реализуется."""

from typing import Any

from app.config import get_settings

MOCK_OIDS: dict[str, float | int | str] = {
    "1.3.6.1.2.1.1.3.0": 4320000,
    "mock.ipo.occupancyPct": 8.5,
    "mock.ipo.sysName": "ipo-lab",
}


class IpoSnmpConnector:
    name = "ipo_snmp"

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def poll_health(self) -> dict[str, Any]:
        settings = get_settings()
        if settings.use_fixtures and (
            not settings.enable_live_connectors or not settings.ipo_snmp_host
        ):
            return {
                "status": "ok",
                "connector": self.name,
                "source": "mock_oid",
                "occupancy_pct": float(MOCK_OIDS["mock.ipo.occupancyPct"]),
                "oids": dict(MOCK_OIDS),
            }
        if not settings.enable_live_connectors or not settings.ipo_snmp_host:
            return {"status": "idle", "connector": self.name, "reason": "live_disabled"}
        return {"status": "skipped", "connector": self.name, "reason": "live_snmp_not_in_v1"}

    async def ingest_once(self) -> list[dict[str, Any]]:
        return []
