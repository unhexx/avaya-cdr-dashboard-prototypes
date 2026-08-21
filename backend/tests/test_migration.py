"""Миграция 0001 содержит обязательные объекты схемы."""

from pathlib import Path

MIGRATION = Path(__file__).resolve().parents[1] / "alembic" / "versions" / "0001_initial_schema.py"


def test_initial_migration_has_enums_and_tables() -> None:
    text = MIGRATION.read_text(encoding="utf-8")
    for token in (
        "call_direction",
        "call_disposition",
        "pbx_kind",
        "log_kind",
        "CREATE TABLE pbx_nodes",
        "CREATE TABLE cdr_records",
        "CREATE TABLE health_snapshots",
        "CREATE TABLE alarms",
        "CREATE TABLE dialplan_entries",
        "CREATE TABLE log_events",
        "CREATE TABLE recording_meta",
        "uq_cdr_dedupe",
        "GENERATED ALWAYS AS",
        "encryption_hint",
    ):
        assert token in text, f"в миграции нет {token}"
