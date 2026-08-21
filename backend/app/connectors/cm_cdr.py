"""TCP-сервер IP-CDR CM. В v1 не стартует, пока ENABLE_LIVE_CONNECTORS=false."""

from typing import Any


class CmCdrConnector:
    name = "cm_cdr"

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def poll_health(self) -> dict[str, Any]:
        return {"status": "idle", "connector": self.name}

    async def ingest_once(self) -> list[dict[str, Any]]:
        return []
