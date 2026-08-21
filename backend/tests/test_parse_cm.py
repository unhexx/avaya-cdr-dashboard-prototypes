"""Золотые фикстуры Communication Manager CDR."""

from datetime import date
from pathlib import Path

from app.parsers.cdr_cm import detect_cm_format, parse_cm_text, parse_customized, parse_expanded
from app.parsers.common import sha256_raw

FIXTURES = Path(__file__).resolve().parents[2] / "docs" / "fixtures" / "cm"


def _read(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_detect_formats() -> None:
    assert detect_cm_format(_read("unformatted.txt")) == "unformatted"
    assert detect_cm_format(_read("expanded.txt")) == "expanded"
    assert detect_cm_format(_read("customized.txt")) == "customized"


def test_unformatted_maps_duration_and_condition() -> None:
    rows = parse_cm_text(_read("unformatted.txt"), default_day=date(2026, 8, 21))
    assert len(rows) == 4
    first = rows[0]
    assert first.duration_seconds == 83
    assert first.direction == "inbound"
    assert first.disposition == "answered"
    assert first.calling_number == "79031234567"
    assert first.dialed_number == "84951234567"
    abandoned = rows[1]
    assert abandoned.disposition == "abandoned"
    assert abandoned.duration_seconds == 0


def test_expanded_keeps_ucid_and_trunks() -> None:
    rows = parse_expanded(_read("expanded.txt"))
    assert len(rows) == 5
    first = rows[0]
    assert first.ucid == "00001001234567890123"
    assert first.trunk_in == "T007"
    assert first.trunk_out == "T001"
    assert first.source_system == "cm"
    conf = [r for r in rows if r.condition_code == "A"][0]
    assert conf.disposition == "conferenced"
    assert conf.is_conferenced is True


def test_customized_header_mapping() -> None:
    rows = parse_customized(_read("customized.txt"))
    assert len(rows) == 4
    no_answer = rows[-1]
    assert no_answer.disposition == "no_answer"
    assert no_answer.ucid == "00001001234567890128"


def test_raw_hash_stable() -> None:
    raw = "08/21/26 14:30 00:01:23 9"
    assert len(sha256_raw(raw)) == 64
    assert sha256_raw(raw) == sha256_raw(raw)
