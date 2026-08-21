# SPRINTPLAN.md

**Sprint:** P0 backend scaffold  
**Status:** IN_PROGRESS (D0 docs done; P0 this fire)  
**Goal:** Land the complete documentation set on `origin/main` so the next fire can implement connectors without inventing product law.

## This Sprint

- [x] Read git state, existing `docs/PROJECT_SPECIFICATION.md` v1.0 (UI prototypes).
- [x] Write root agent files: `AGENTS.md`, `README.md`, `LICENSE`, `.gitignore`, `.env.example`, `Agent-Init.sh`, `SYSTEM_PROMPT.md`, `TASK_SPECIFICATION.md`, `DEVELOPMENT_STANDARDS.md`, `prompts/short_orchestrator_prompt.md`.
- [x] Write `docs/*` package listed in the constitution index (v2.0).
- [x] Write ADRs 0001–0011.
- [x] Write fixtures under `docs/fixtures/{smdr,cm,syslog,sql,recordings}`.
- [x] Write `.agent/{PLAN.md,TODO.md,project_config.json}`, `SPRINTPLAN.md`, `PROJECT_CONTEXT.md`.
- [x] Shields.io badges on README (`style=flat-square`, public `img.shields.io`).
- [x] Commit in natural Russian, push `main`.

## Next Sprint (not this fire)

- P0 backend scaffold + docker-compose + Alembic CDR schema.
- P1 CDR/SMDR parsers + fixture ingest.
- Then health, dialplan, logs, recordings, UI per `docs/TASKS.md`.

## Out of Sprint

- Application code (FastAPI routes, React views) — docs-only fire.
- Live PBX sessions.
- SysMonitor, recording decryption.
