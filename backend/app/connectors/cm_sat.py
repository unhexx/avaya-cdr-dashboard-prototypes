"""SAT по SSH: в v1 live-сессия не открывается, только allowlist + фикстуры."""

from typing import Any

from app.config import get_settings
from app.parsers.sat_health import is_sat_allowed


class CmSatConnector:
    name = "cm_sat"

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def poll_health(self) -> dict[str, Any]:
        settings = get_settings()
        if not settings.enable_live_connectors or not settings.cm_sat_host:
            return {
                "status": "idle",
                "connector": self.name,
                "reason": "live_disabled" if not settings.enable_live_connectors else "no_host",
            }
        # Живой SSH SAT сознательно не реализован в этом срезе.
        return {"status": "skipped", "connector": self.name, "reason": "live_sat_not_in_this_slice"}

    async def ingest_once(self) -> list[dict[str, Any]]:
        return []

    def allow_command(self, command: str) -> bool:
        return is_sat_allowed(command)
