"""Конституция: в коде бэкенда нет клиента SysMonitor."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "app"


def test_no_sysmonitor_implementation() -> None:
    hits: list[str] = []
    for path in ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        if "sysmonitor" in text and "запрещ" not in text and "не реализуется" not in text:
            hits.append(str(path))
    assert hits == [], f"подозрение на SysMonitor: {hits}"
