# ACCEPTANCE — first release (v1)

All boxes must be true on `origin/main` for STOP=DONE.

## Docs

- [x] Root: `AGENTS.md` `README.md` `LICENSE` `.gitignore` `.env.example` `Agent-Init.sh` `SYSTEM_PROMPT.md` `TASK_SPECIFICATION.md` `DEVELOPMENT_STANDARDS.md` `prompts/short_orchestrator_prompt.md`
- [x] `docs/PROJECT_SPECIFICATION.md` is v2.0 index
- [x] Constitution, product, architecture, data model, API, connectors, Avaya, dialplan, logs, recordings, UI, security, testing, deployment, acceptance, roadmap, agent guide, tasks, changelog, status
- [x] ADRs 0001–0011
- [x] Fixtures: smdr, cm, syslog, sql, recordings
- [x] `.agent/PLAN.md` `.agent/TODO.md` `.agent/project_config.json`
- [x] README badges are Shields.io `style=flat-square` on `https://img.shields.io`

## Runtime

- [x] `docker compose up --build` starts api + postgres + web
- [x] `GET /api/health` returns 200 with `fixtures` flag
- [x] `POST /api/ingest/fixtures` loads CDR, logs, dialplan, recordings meta
- [x] `GET /api/cdr` filters, paginates, returns `raw_record` on detail
- [x] `GET /api/export?format=csv` downloads
- [x] `GET /api/pbx` and `/api/pbx/{id}/health` from mock
- [x] `GET /api/dialplan` returns fixture ARS/IPO rows
- [x] `GET /api/logs?kind=sip` and `kind=e1` return fixture lines
- [x] Unencrypted `GET /api/recordings/{id}/audio` is 200 audio
- [x] Encrypted IPO fixture audio is **409** with `reason=ipo_encrypted_r11`
- [x] No SysMonitor client in the tree (`rg -i sysmonitor` only hits docs forbidding it)
- [x] Optional HTTP Basic: `APP_BASIC_AUTH_USER` set → 401 without creds; unset → open API

## UI

- [x] Four views route and render fixture CDR
- [x] Health / Dialplan / Logs / Recordings pages exist
- [x] Russian default strings; English toggle
- [x] Encrypted recording shows explanation, not a broken `<audio>`

## Quality

- [x] `pytest` green with `USE_FIXTURES=true` and no live hosts
- [ ] Frontend unit tests green (Vitest not wired in v1)
- [x] ruff + mypy (backend) clean on the slice that introduced code
- [x] Identifiers English; new comments Russian
- [x] No `.env`, no customer audio, no real numbers (fixtures only)
- [x] `.github/workflows/ci.yml` runs pytest, ruff, mypy, frontend build

## Git

- [x] Slice commits in natural Russian
- [x] `main` pushed to `origin`
