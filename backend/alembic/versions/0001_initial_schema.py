"""Начальная каноническая схема PostgreSQL (docs/DATA_MODEL.md).

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-21
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# asyncpg не принимает несколько команд в одном prepared statement.
_UPGRADE_STMTS = [
    """
    CREATE TYPE call_direction AS ENUM (
        'inbound', 'outbound', 'internal', 'tandem', 'unknown'
    )
    """,
    """
    CREATE TYPE call_disposition AS ENUM (
        'answered', 'abandoned', 'busy', 'no_answer', 'failed',
        'transferred', 'conferenced', 'other'
    )
    """,
    """
    CREATE TYPE pbx_kind AS ENUM (
        'cm', 'ipo', 'session_manager', 'sbce', 'other'
    )
    """,
    "CREATE TYPE log_kind AS ENUM ('sip', 'e1', 'alarm', 'sat', 'other')",
    """
    CREATE TABLE pbx_nodes (
        id           SERIAL PRIMARY KEY,
        name         VARCHAR(64) NOT NULL,
        kind         pbx_kind NOT NULL,
        host         VARCHAR(255),
        enabled      BOOLEAN NOT NULL DEFAULT TRUE,
        extra        JSONB NOT NULL DEFAULT '{}'::jsonb
    )
    """,
    """
    CREATE TABLE cdr_records (
        id                    BIGSERIAL PRIMARY KEY,
        ucid                  VARCHAR(32),
        call_id               VARCHAR(32),
        start_time            TIMESTAMPTZ NOT NULL,
        answer_time           TIMESTAMPTZ,
        end_time              TIMESTAMPTZ,
        duration_seconds      INTEGER NOT NULL DEFAULT 0,
        ring_duration_seconds INTEGER NOT NULL DEFAULT 0,
        hold_duration_seconds INTEGER NOT NULL DEFAULT 0,
        park_duration_seconds INTEGER NOT NULL DEFAULT 0,
        total_duration_seconds INTEGER GENERATED ALWAYS AS (
            duration_seconds + ring_duration_seconds
            + COALESCE(hold_duration_seconds, 0)
            + COALESCE(park_duration_seconds, 0)
        ) STORED,
        calling_number        VARCHAR(32),
        dialed_number         VARCHAR(64),
        connected_number      VARCHAR(64),
        direction             call_direction NOT NULL DEFAULT 'unknown',
        disposition           call_disposition NOT NULL DEFAULT 'other',
        condition_code        VARCHAR(8),
        access_code_dialed    VARCHAR(8),
        access_code_used      VARCHAR(8),
        trunk_in              VARCHAR(16),
        trunk_out             VARCHAR(16),
        account_code          VARCHAR(32),
        auth_code             VARCHAR(16),
        vdn                   VARCHAR(16),
        node_number           VARCHAR(8),
        agent_extension       VARCHAR(16),
        agent_id              VARCHAR(16),
        skill_group           VARCHAR(16),
        is_internal           BOOLEAN NOT NULL DEFAULT FALSE,
        is_transferred        BOOLEAN NOT NULL DEFAULT FALSE,
        is_conferenced        BOOLEAN NOT NULL DEFAULT FALSE,
        source_system         VARCHAR(64) NOT NULL DEFAULT 'mock',
        pbx_node_id           INTEGER REFERENCES pbx_nodes(id),
        raw_record            TEXT,
        raw_hash              CHAR(64),
        created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE UNIQUE INDEX uq_cdr_dedupe ON cdr_records (source_system, raw_hash)",
    "CREATE INDEX idx_cdr_start_time ON cdr_records (start_time DESC)",
    "CREATE INDEX idx_cdr_calling ON cdr_records (calling_number)",
    "CREATE INDEX idx_cdr_dialed ON cdr_records (dialed_number)",
    "CREATE INDEX idx_cdr_direction ON cdr_records (direction)",
    "CREATE INDEX idx_cdr_disposition ON cdr_records (disposition)",
    "CREATE INDEX idx_cdr_vdn ON cdr_records (vdn)",
    "CREATE INDEX idx_cdr_agent ON cdr_records (agent_extension)",
    "CREATE INDEX idx_cdr_ucid ON cdr_records (ucid)",
    """
    CREATE TABLE health_snapshots (
        id            BIGSERIAL PRIMARY KEY,
        pbx_node_id   INTEGER NOT NULL REFERENCES pbx_nodes(id),
        taken_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        status        VARCHAR(16) NOT NULL,
        occupancy_pct NUMERIC(5,2),
        details       JSONB NOT NULL DEFAULT '{}'::jsonb
    )
    """,
    """
    CREATE TABLE alarms (
        id            BIGSERIAL PRIMARY KEY,
        pbx_node_id   INTEGER REFERENCES pbx_nodes(id),
        raised_at     TIMESTAMPTZ NOT NULL,
        cleared_at    TIMESTAMPTZ,
        severity      VARCHAR(16) NOT NULL,
        code          VARCHAR(32),
        resource      VARCHAR(64),
        message       TEXT NOT NULL,
        raw           TEXT
    )
    """,
    """
    CREATE TABLE dialplan_entries (
        id            BIGSERIAL PRIMARY KEY,
        pbx_node_id   INTEGER REFERENCES pbx_nodes(id),
        source        VARCHAR(32) NOT NULL,
        match_prefix  VARCHAR(32) NOT NULL,
        min_digits    INTEGER,
        max_digits    INTEGER,
        route         VARCHAR(64),
        location      VARCHAR(32),
        raw           TEXT,
        synced_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX idx_dialplan_prefix ON dialplan_entries (match_prefix)",
    """
    CREATE TABLE log_events (
        id            BIGSERIAL PRIMARY KEY,
        pbx_node_id   INTEGER REFERENCES pbx_nodes(id),
        kind          log_kind NOT NULL DEFAULT 'other',
        event_time    TIMESTAMPTZ NOT NULL,
        host          VARCHAR(128),
        severity      VARCHAR(16),
        call_id       VARCHAR(64),
        sip_method    VARCHAR(16),
        sip_response  INTEGER,
        ds1_board     VARCHAR(32),
        alarm_type    VARCHAR(16),
        message       TEXT NOT NULL,
        raw           TEXT
    )
    """,
    "CREATE INDEX idx_log_time ON log_events (event_time DESC)",
    "CREATE INDEX idx_log_kind ON log_events (kind, event_time DESC)",
    """
    CREATE TABLE recording_meta (
        id              BIGSERIAL PRIMARY KEY,
        ucid            VARCHAR(32),
        cdr_id          BIGINT REFERENCES cdr_records(id),
        start_time      TIMESTAMPTZ NOT NULL,
        duration_seconds INTEGER,
        calling_number  VARCHAR(32),
        dialed_number   VARCHAR(64),
        filename        VARCHAR(512),
        mime_type       VARCHAR(64),
        encrypted       BOOLEAN NOT NULL DEFAULT FALSE,
        encryption_hint VARCHAR(64),
        sql_source_id   VARCHAR(64),
        extra           JSONB NOT NULL DEFAULT '{}'::jsonb
    )
    """,
    "CREATE INDEX idx_rec_ucid ON recording_meta (ucid)",
    "CREATE INDEX idx_rec_time ON recording_meta (start_time DESC)",
]

_DOWNGRADE_STMTS = [
    "DROP TABLE IF EXISTS recording_meta",
    "DROP TABLE IF EXISTS log_events",
    "DROP TABLE IF EXISTS dialplan_entries",
    "DROP TABLE IF EXISTS alarms",
    "DROP TABLE IF EXISTS health_snapshots",
    "DROP TABLE IF EXISTS cdr_records",
    "DROP TABLE IF EXISTS pbx_nodes",
    "DROP TYPE IF EXISTS log_kind",
    "DROP TYPE IF EXISTS pbx_kind",
    "DROP TYPE IF EXISTS call_disposition",
    "DROP TYPE IF EXISTS call_direction",
]


def upgrade() -> None:
    for stmt in _UPGRADE_STMTS:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in _DOWNGRADE_STMTS:
        op.execute(stmt)
