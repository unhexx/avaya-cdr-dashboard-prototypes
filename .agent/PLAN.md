# PLAN

## Goal

First-release Avaya operations dashboard (health, CDR/SMDR, dialplan, SIP/E1 logs, recordings sql-source) with max official-interface compatibility. No SysMonitor reverse. Encrypted IPO ≥ R11.1 → 409.

## Phase D0 — Docs (this fire)

Land the complete docs package on `origin/main`. No application code.

## Phase P0 — Scaffold (next)

FastAPI + compose + Alembic + `/api/health`.

## Phase P2 Health (this fire)

SAT mock snapshots, alarms, SNMP stubs, `/health` UI.

## Phase P3+

Dialplan → logs → recordings → UI → harden. One INVEST per fire. See `docs/TASKS.md` and `.agent/TODO.md`.

## Risks

- Primary checkout may be root-owned; push from a writable clone.
- Customized CM CDR delimiters differ per site — fixtures cover `|`; parser must auto-detect.
