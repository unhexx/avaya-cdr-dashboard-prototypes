# TASKS

INVEST backlog. Execution copy with checkboxes: `.agent/TODO.md`.

## D0 — Docs package (current)

- Root agent files, docs index v2.0, ADRs 0001–0011, fixtures, `.agent/*`, Shields README.

## P0 — Scaffold

- `backend/` FastAPI app, Pydantic settings, `/api/health`
- `docker-compose.yml` postgres + api + web
- Alembic initial migration (full `DATA_MODEL.md`)
- pyproject.toml, ruff, mypy, pytest skeleton

## P1 — CDR ingest

- CM unformatted/expanded/customized parsers + fixtures
- IPO SMDR header-based parser + fixtures
- TCP listen/client connectors
- `GET /api/cdr`, detail, export CSV/JSON, mock-generate
- Dedup on `raw_hash`

## P2 — Health

- `pbx_nodes`, snapshots, alarms
- Mock health from SAT fixture text
- SNMP stub (skip live)
- `/health` UI page

## P3 — Dialplan

- Parse `list ars analysis` + IPO shortcodes
- `/api/dialplan` + longest-prefix search
- `/dialplan` UI

## P4 — SIP / E1 logs

- Syslog listener + classifiers
- `/api/logs` + `/logs` UI

## P5 — Recordings

- sql-source adapter (MariaDB + PG)
- Fixture SQL + JSON
- Audio 200 / encrypted 409
- `/recordings` UI + player banner

## P6 — UI four views

- Classic table virtualized
- Analytics KPIs + Recharts
- Contact-center SLA / heatmap
- Modern cards + timeline
- i18n ru/en

## P7 — Harden

- Basic auth optional
- SAT allowlist tests
- Compose smoke in CI
- ACCEPTANCE walkthrough
