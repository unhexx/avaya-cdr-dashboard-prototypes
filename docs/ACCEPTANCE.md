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
- [ ] `POST /api/ingest/fixtures` loads CDR, logs, dialplan, recordings meta
- [x] `GET /api/cdr` filters, paginates, returns `raw_record` on detail
- [x] `GET /api/export?format=csv` downloads
- [x] `GET /api/pbx` and `/api/pbx/{id}/health` from mock
- [ ] `GET /api/dialplan` returns fixture ARS/IPO rows
- [ ] `GET /api/logs?kind=sip` and `kind=e1` return fixture lines
- [ ] Unencrypted `GET /api/recordings/{id}/audio` is 200 audio
- [ ] Encrypted IPO fixture audio is **409** with `reason=ipo_encrypted_r11`
- [x] No SysMonitor client in the tree (`rg -i sysmonitor` only hits docs forbidding it)

## UI

- [ ] Four views route and render fixture CDR
- [ ] Health / Dialplan / Logs / Recordings pages exist
- [ ] Russian default strings; English toggle
- [ ] Encrypted recording shows explanation, not a broken `<audio>`

## Quality

- [x] `pytest` green with `USE_FIXTURES=true` and no live hosts
- [ ] Frontend unit tests green
- [x] ruff + mypy (backend) clean on the slice that introduced code
- [x] Identifiers English; new comments Russian
- [ ] No `.env`, no customer audio, no real numbers

## Git

- [x] Slice commits in natural Russian
- [x] `main` pushed to `origin`
