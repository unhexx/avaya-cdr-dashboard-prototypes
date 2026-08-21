"""Загрузка фикстур CM/IPO и генерация mock-CDR."""

from __future__ import annotations

import random
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from app.parsers.cdr_cm import parse_cm_text
from app.parsers.smdr_ipo import parse_smdr_csv
from app.parsers.types import NormalizedCdr
from app.services.cdr_repo import CdrRepository


def find_fixtures_root() -> Path:
    here = Path(__file__).resolve()
    candidates = [
        Path("/srv/docs/fixtures"),
        Path.cwd() / "docs" / "fixtures",
        here.parents[3] / "docs" / "fixtures",
        here.parents[2] / "docs" / "fixtures",
    ]
    for path in candidates:
        if path.is_dir():
            return path
    raise FileNotFoundError("docs/fixtures not found")


def load_fixture_cdrs(root: Path | None = None) -> list[NormalizedCdr]:
    base = root or find_fixtures_root()
    rows: list[NormalizedCdr] = []
    cm_dir = base / "cm"
    if cm_dir.is_dir():
        for path in sorted(cm_dir.glob("*.txt")):
            text = path.read_text(encoding="utf-8")
            rows.extend(parse_cm_text(text, default_day=date(2026, 8, 21)))
    smdr_dir = base / "smdr"
    if smdr_dir.is_dir():
        csv_path = smdr_dir / "ipo-r11.csv"
        if csv_path.is_file():
            rows.extend(parse_smdr_csv(csv_path.read_text(encoding="utf-8")))
    return rows


async def ingest_fixtures(repo: CdrRepository, root: Path | None = None) -> dict[str, int]:
    rows = load_fixture_cdrs(root)
    stats = await repo.insert_many(rows)
    stats["parsed"] = len(rows)
    return stats


def generate_mock_cdrs(n: int) -> list[NormalizedCdr]:
    count = max(1, min(n, 10_000))
    rng = random.Random(42)
    now = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)
    directions = ["inbound", "outbound", "internal"]
    dispositions = ["answered", "abandoned", "busy", "no_answer"]
    rows: list[NormalizedCdr] = []
    for i in range(count):
        start = now - timedelta(minutes=rng.randint(0, 24 * 60))
        duration = rng.choice([0, 12, 45, 83, 120, 240])
        direction = directions[i % 3]
        disposition = dispositions[0] if duration else dispositions[1]
        calling = f"7903123{4000 + (i % 500):04d}"
        dialed = f"12{(i % 80):02d}"
        raw = f"mock,{i},{start.isoformat()},{calling},{dialed},{duration}"
        rows.append(
            NormalizedCdr(
                start_time=start,
                duration_seconds=duration,
                calling_number=calling,
                dialed_number=dialed,
                direction=direction,
                disposition=disposition,
                agent_extension=dialed if direction == "inbound" else None,
                ucid=f"{i:020d}",
                raw_record=raw,
                source_system="mock",
            )
        )
    return rows
