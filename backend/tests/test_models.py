"""Канонические таблицы присутствуют в метаданных ORM."""

from app.models import Base

REQUIRED_TABLES = {
    "pbx_nodes",
    "cdr_records",
    "health_snapshots",
    "alarms",
    "dialplan_entries",
    "log_events",
    "recording_meta",
}


def test_metadata_contains_canonical_tables() -> None:
    names = set(Base.metadata.tables)
    missing = REQUIRED_TABLES - names
    assert not missing, f"нет таблиц: {missing}"


def test_cdr_has_raw_record_and_hash() -> None:
    table = Base.metadata.tables["cdr_records"]
    assert "raw_record" in table.c
    assert "raw_hash" in table.c
    assert "ucid" in table.c
