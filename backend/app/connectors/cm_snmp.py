"""SNMP v2c Communication Manager. Живой опрос в v1 пропускается (stub)."""

from typing import Any

from app.config import get_settings

# Искусственные OID для mock; не выдаём их за enterprise MIB Avaya.
MOCK_OIDS: dict[str, float | int | str] = {
    "1.3.6.1.2.1.1.3.0": 8640000,  # sysUpTime (сотые секунды)
    "mock.cm.occupancyPct": 12.0,
    "mock.cm.alarmsMinor": 1,
}


class CmSnmpConnector:
    name = "cm_snmp"

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def poll_health(self) -> dict[str, Any]:
        settings = get_settings()
        if settings.use_fixtures and (
            not settings.enable_live_connectors or not settings.cm_snmp_host
        ):
            return {
                "status": "ok",
                "connector": self.name,
                "source": "mock_oid",
                "occupancy_pct": float(MOCK_OIDS["mock.cm.occupancyPct"]),
                "oids": dict(MOCK_OIDS),
            }
        if not settings.enable_live_connectors or not settings.cm_snmp_host:
            return {"status": "idle", "connector": self.name, "reason": "live_disabled"}
        return {"status": "skipped", "connector": self.name, "reason": "live_snmp_not_in_v1"}

    async def ingest_once(self) -> list[dict[str, Any]]:
        return []
