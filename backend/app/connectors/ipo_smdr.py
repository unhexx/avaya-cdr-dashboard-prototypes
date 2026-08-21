"""TCP-клиент SMDR IP Office. Idle без IPO_SMDR_HOST. SysMonitor не реализуется."""

from typing import Any


class IpoSmdrConnector:
    name = "ipo_smdr"

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def poll_health(self) -> dict[str, Any]:
        return {"status": "idle", "connector": self.name}

    async def ingest_once(self) -> list[dict[str, Any]]:
        return []
