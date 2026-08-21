# ARCHITECTURE

## Overview

```
 Avaya CM IP-CDR TCP          IPO SMDR TCP           syslog UDP/TCP
        │                          │                        │
        ▼                          ▼                        ▼
 ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
 │ connector.cm │          │ connector.ipo│          │ connector.log│
 └──────┬───────┘          └──────┬───────┘          └──────┬───────┘
        │                          │                        │
        ▼                          ▼                        ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ parsers (cdr_cm, smdr_ipo, syslog_sip, syslog_ds1)               │
 └────────────────────────────┬─────────────────────────────────────┘
                              ▼
                    PostgreSQL (canonical)
                              ▲
          SAT/SNMP/SSA ───────┤ snapshots, dialplan dumps
          sql-source ─────────┤ recording_meta (MariaDB or PG, read-only)
                              ▼
                         FastAPI
                              ▼
                      Vite SPA (React)
```

Mock connectors implement the same interfaces and read `docs/fixtures/**`. `USE_FIXTURES=true` is the CI default.

## Processes

| Process | Role |
|---|---|
| `backend` (uvicorn) | API, ingest loops, SAT poller, sql-source reader |
| `frontend` (nginx or vite preview) | SPA |
| `postgres` | Canonical store |
| `mariadb` (optional compose profile `recordings`) | Fixture sql-source |
| `redis` (optional) | Cache for stats |

## Backend packages

```
backend/app/
  api/            # routers: health, cdr, dialplan, logs, recordings, export
  connectors/     # ProtocolConnector ABC + cm, ipo, snmp, syslog, sat, sql_recordings, mock
  parsers/        # pure functions, no I/O
  models/         # SQLAlchemy
  schemas/        # Pydantic
  services/       # ingest, search, health_aggregate
  config.py       # Pydantic Settings
```

## Connector ABC (normative sketch)

```python
class ProtocolConnector(Protocol):
    name: str
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def poll_health(self) -> HealthSnapshot: ...
    async def ingest_once(self) -> Sequence[NormalizedEvent]: ...
```

Live connectors no-op when host env is empty; mock connector always runs in CI.

## SAT poller

Periodic (default 60s) SSH session, **allowlisted commands only**, parse text, write `health_snapshots` and `dialplan_entries`. Timeouts hard-kill the channel. No interactive SAT menus.

## Ingest

TCP servers (CM CDR, syslog) and TCP clients (IPO SMDR) write to an asyncio queue; a single consumer persists batches. Duplicate key: `(source_system, ucid or raw_hash, start_time)` — insert ignore.

## Frontend

One SPA, routes:

| Path | View |
|---|---|
| `/` | Classic table (prototype 1) |
| `/analytics` | KPI + charts (prototype 2) |
| `/cc` | Contact-center (prototype 3) |
| `/cards` | Modern cards + timeline (prototype 4) |
| `/health` | PBX health |
| `/dialplan` | Dialplan search |
| `/logs` | SIP / E1 syslog |
| `/recordings` | Recording list + player |

Shared filter store (Zustand) syncs table and charts.

## Trust boundaries

- Browser never talks to SAT/SMDR directly.
- sql-source credentials are server-side, read-only DB user.
- Audio files streamed from backend after ACL check (single-tenant = authenticated session if basic auth enabled).
