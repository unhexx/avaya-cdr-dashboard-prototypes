"""ABC коннектора. Живые хосты пустые → no-op. SysMonitor не реализуется."""

from collections.abc import Sequence
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolConnector(Protocol):
    """Единый контракт ingest/health (ADR 0003)."""

    name: str

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    async def poll_health(self) -> dict[str, Any]: ...

    async def ingest_once(self) -> Sequence[dict[str, Any]]: ...
