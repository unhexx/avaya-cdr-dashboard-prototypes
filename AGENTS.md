# AGENTS.md — Instructions for Coding Agents

This repository is structured so coding agents can take Avaya CDR Dashboard from empty tree to first release without a human in the loop.

## Project Goal

Build a production-ready operations dashboard with **maximum Avaya compatibility**:

1. **PBX health** — CM, IP Office, Session Manager, SBCE (alarms, trunks, occupancy, DS1/E1, SIP)
2. **CDR ingest + search** — Communication Manager IP-CDR (unformatted / expanded / customized) and IP Office SMDR CSV
3. **Dialplan** — ARS / dialplan analysis (CM SAT) and IPO dial-plan dump
4. **SIP / E1 logs** — syslog from SM, CM MEDPRO, SBCE; DS1 alarms
5. **On-demand recordings** — metadata + audio via **MariaDB / PostgreSQL sql-source**; encrypted IPO ≥ R11.1 → HTTP 409 meta-only

UI language: Russian primary, English i18n. Four views from the original prototypes (classic table, analytics, contact-center, modern cards) plus Health / Dialplan / Logs / Recordings.

## Current Status

Read `docs/STATUS.md` and `.agent/TODO.md`. Spec index: [`docs/PROJECT_SPECIFICATION.md`](docs/PROJECT_SPECIFICATION.md) (v2.0).

Closed-loop bootstrap (Linux): `bash Agent-Init.sh` then `source .venv/bin/activate`. First session message: [`prompts/short_orchestrator_prompt.md`](prompts/short_orchestrator_prompt.md).

## Recommended Stack (do not deviate without an ADR)

| Layer | Choice (ADR 0001) |
|---|---|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2 |
| Canonical DB | PostgreSQL 16 |
| Recordings source | MariaDB 10.11+ **or** PostgreSQL (read-only sql-source) |
| Cache | Redis optional |
| Frontend | React 18, TypeScript, Vite, Tailwind, shadcn/ui, TanStack Table/Query |
| Charts | Recharts |
| Containers | Docker Compose |
| Tests | pytest + pytest-asyncio (backend), Vitest (frontend) |
| Lint | ruff + mypy (strict) / ESLint |

Frontend already scaffolded under `frontend/`. Backend lives under `backend/` (to be created in the first code slice).

## Directory Layout (target)

```
avaya-cdr-dashboard-prototypes/
├── backend/                 # FastAPI app
│   ├── app/
│   │   ├── api/
│   │   ├── connectors/      # cm, ipo, syslog, snmp, sql_recordings, mock
│   │   ├── parsers/         # cdr_cm, smdr_ipo
│   │   ├── models/
│   │   ├── services/
│   │   └── config.py
│   └── tests/
├── frontend/                # Vite SPA (exists)
├── docs/                    # this package
│   ├── adr/
│   └── fixtures/{smdr,cm,syslog,sql,recordings}
├── docker-compose.yml
├── .env.example
├── Agent-Init.sh
├── AGENTS.md
└── README.md
```

## Exact Commands

```bash
bash Agent-Init.sh
source .venv/bin/activate

# backend (after pyproject exists)
uv sync --all-extras
ruff check . --fix && ruff format .
mypy backend
pytest -q

# frontend
cd frontend && npm test && npm run build

# stack
docker compose up --build
```

## Boundaries — NEVER

- Reverse-engineer **SysMonitor** or undocumented binary diagnostic protocols (ADR 0004).
- Decrypt IP Office ≥ R11.1 encrypted recordings. Return **409** + metadata (ADR 0005).
- Issue SAT `change` / `add` / `remove` / `busyout` / `release` in v1 (read-only allowlist).
- Commit `.env`, secrets, customer CDR, or real audio.
- Require a live PBX for CI (ADR 0006).
- Invent HTML/CSS README badges. Shields.io `style=flat-square` only.

## Preferred Development Loop

1. `bash Agent-Init.sh` and `source .venv/bin/activate`
2. Read `.agent/TODO.md` + `docs/STATUS.md` + `docs/TASKS.md`
3. Take the next unfinished INVEST item only
4. Ambiguous fork → ADR, lock one option
5. Tests against `docs/fixtures/**`
6. Commit in natural Russian; identifiers English
7. Merge to `main` and push when the slice is green

## Spec map

| Need | Doc |
|---|---|
| Laws | `docs/CONSTITUTION.md` |
| What we ship | `docs/PRODUCT.md` |
| How it is built | `docs/ARCHITECTURE.md` |
| Schema | `docs/DATA_MODEL.md` |
| HTTP | `docs/API.md` |
| Avaya | `docs/INTEGRATION_AVAYA.md`, `docs/CONNECTORS.md` |
| Dialplan / logs / recordings | `docs/DIALPLAN.md`, `docs/LOGS.md`, `docs/RECORDINGS.md` |
| UI | `docs/UI_SPEC.md` |
| Done | `docs/ACCEPTANCE.md` |
| Queue | `docs/TASKS.md`, `.agent/TODO.md` |
