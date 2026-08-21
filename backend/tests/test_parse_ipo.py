"""SMDR IP Office по заголовкам CSV."""

from pathlib import Path

from app.parsers.smdr_ipo import parse_smdr_csv

CSV = Path(__file__).resolve().parents[2] / "docs" / "fixtures" / "smdr" / "ipo-r11.csv"


def test_smdr_header_based() -> None:
    rows = parse_smdr_csv(CSV.read_text(encoding="utf-8"))
    assert len(rows) == 6
    first = rows[0]
    assert first.source_system == "ipo"
    assert first.direction == "inbound"
    assert first.duration_seconds == 83
    assert first.ring_duration_seconds == 12
    assert first.ucid == "00001001234567890123"
    assert first.agent_extension == "1205"
    outbound = rows[2]
    assert outbound.direction == "outbound"
    assert outbound.account_code == "SALES-42"
    internal = rows[3]
    assert internal.direction == "internal"
    transferred = rows[4]
    assert transferred.is_transferred is True
    assert transferred.vdn == "3001"
    abandoned = rows[1]
    assert abandoned.disposition == "abandoned"
