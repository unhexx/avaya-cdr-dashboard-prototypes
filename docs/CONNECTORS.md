# CONNECTORS

Every external system is a `ProtocolConnector`. Live host empty → connector stays idle. Mock is always registered.

## Pack (v1)

| Name | Direction | Transport | Fixture |
|---|---|---|---|
| `mock` | in | files | `docs/fixtures/**` |
| `cm_cdr` | in | TCP listen (IP-CDR printer) | `docs/fixtures/cm/` |
| `cm_sat` | poll | SSH SAT, read-only allowlist | parsed text in `docs/fixtures/cm/sat/` |
| `cm_snmp` | poll | SNMP v2c | mock OIDs |
| `ipo_smdr` | in | TCP client to IPO:8888 | `docs/fixtures/smdr/` |
| `ipo_snmp` | poll | SNMP v2c | mock |
| `ipo_ssa` | poll | HTTPS SSA XML (documented) | fixture XML |
| `syslog` | in | UDP/TCP listen | `docs/fixtures/syslog/` |
| `sql_recordings` | poll | MariaDB or PostgreSQL read-only | `docs/fixtures/sql/` |

## Rules

- No SysMonitor connector. A PR that adds `sysmonitor` or a binary IPO diagnostic codec is rejected (ADR 0004).
- Connectors **parse via `backend/app/parsers`**, they do not embed format logic.
- Each connector exposes `poll_health()` even if it only returns `{status: "idle"}`.
- Backoff: 1s, 5s, 30s, cap 60s on connection errors. Structured logs (`connector`, `peer`, `error`).
- TLS: SAT SSH host key policy = accept-and-pin to `.env` fingerprint when provided; otherwise warn once in dev.

## Mock connector

`POST /api/ingest/fixtures` walks:

1. `docs/fixtures/cm/*.txt` → CM parser  
2. `docs/fixtures/smdr/*.csv` → IPO parser  
3. `docs/fixtures/syslog/*.log` → log parser  
4. `docs/fixtures/sql/*.sql` → recording_meta (or JSON sibling)  
5. `docs/fixtures/cm/sat/*.txt` → health + dialplan  

Idempotent: `raw_hash` unique index.

## Adding a connector

1. New module under `backend/app/connectors/`
2. Register in factory
3. Fixture file + parser tests
4. ADR if the protocol is not in this table
