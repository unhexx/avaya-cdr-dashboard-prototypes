# PROJECT_CONTEXT.md

> Source of Truth: `TASK_SPECIFICATION.md` + `docs/PROJECT_SPECIFICATION.md` (v2.0)

## Project Identification

| Parameter | Value |
|-----------|-------|
| **Project** | Avaya CDR Dashboard |
| **Repo** | `avaya-cdr-dashboard-prototypes` |
| **Goal** | First-release operations dashboard: health, CDR/SMDR, dialplan, SIP/E1 logs, recordings sql-source |
| **Tech Stack** | Python 3.12 FastAPI, PostgreSQL 16, MariaDB/PG sql-source, React 18 Vite TS Tailwind |
| **Current Branch** | `main` (docs written on a writable clone if the primary worktree is root-owned) |
| **Template** | agentic_loop_template v3.5.0 (optional symlink) |

## Current Status

| Field | Value |
|-------|-------|
| **Cycle Number** | 1 |
| **Current Phase** | docs-package |
| **Status** | IN_PROGRESS |
| **Confidence** | 0.9 |

## Key Decisions (locked in ADRs)

- Python FastAPI + React Vite, not NestJS (ADR 0001).
- PostgreSQL is the system of record; MariaDB/PG is a read-only recordings source (ADR 0002, 0005).
- Connector plugins; official protocols only (ADR 0003).
- Never reverse SysMonitor (ADR 0004).
- Encrypted IPO ≥ R11.1 recordings → 409 meta-only (ADR 0005).
- Fixtures mandatory for CI (ADR 0006).
- Single-tenant v1 (ADR 0007).
- Syslog + file tail for SIP/E1, not pcap reverse (ADR 0008).
- Dialplan via periodic dump, not real-time (ADR 0009).
- One SPA, four views plus ops pages (ADR 0010).
- English identifiers and product docs; Russian commits and comments (ADR 0011).

## Permanent Rules

- Advance unfinished items from `.agent/PLAN.md` + `.agent/TODO.md` only.
- One INVEST slice per fire.
- SAT v1 is read-only allowlist.
- README badges: Shields.io `style=flat-square` on `https://img.shields.io`.
