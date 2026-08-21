# CHANGELOG

## 0.3.0 — 2026-08-21

### Added

- FastAPI backend: settings, `/api/health`, optional HTTP Basic.
- SQLAlchemy models and Alembic `0001_initial` matching `docs/DATA_MODEL.md`.
- `docker-compose.yml`: postgres + api + web (Aquarius SPA via nginx).
- pytest skeleton (health, settings, schema, no-SysMonitor).

## 0.2.0 — 2026-08-21

### Notes

- Rebased onto the Aquarius UI foundation already on `main` (`docs/BRAND.md`, shared components).

### Added

- Complete first-release documentation package (v2.0 index).
- Constitution, product, architecture, data model, API, connectors, Avaya integration, dialplan, logs, recordings, UI spec, security, testing, deployment, acceptance, roadmap, agent guide, tasks, status.
- ADRs 0001–0011 (locked forks).
- Fixtures for CM CDR, IPO SMDR, syslog SIP/E1, SAT dumps, recordings SQL.
- Agent loop files: `AGENTS.md`, `Agent-Init.sh`, `SYSTEM_PROMPT.md`, `TASK_SPECIFICATION.md`, `DEVELOPMENT_STANDARDS.md`, `.agent/*`.
- MIT license, `.env.example`, `.gitignore`.
- README Shields.io badges.

### Changed

- `docs/PROJECT_SPECIFICATION.md` upgraded from v1.0 (four UI prototypes only) to v2.0 index of the operations dashboard.

## 0.1.0 — 2026-08-21

- Frontend Vite + React + TypeScript + Tailwind scaffold.
- v1.0 prototype specification (CDR model + four UI views).
