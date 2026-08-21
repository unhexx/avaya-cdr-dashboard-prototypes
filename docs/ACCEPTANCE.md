# ACCEPTANCE — first release (v1)

All boxes must be true on `origin/main` for STOP=DONE.

## Docs

- [ ] Root: `AGENTS.md` `README.md` `LICENSE` `.gitignore` `.env.example` `Agent-Init.sh` `SYSTEM_PROMPT.md` `TASK_SPECIFICATION.md` `DEVELOPMENT_STANDARDS.md` `prompts/short_orchestrator_prompt.md`
- [ ] `docs/PROJECT_SPECIFICATION.md` is v2.0 index
- [ ] Constitution, product, architecture, data model, API, connectors, Avaya, dialplan, logs, recordings, UI, security, testing, deployment, acceptance, roadmap, agent guide, tasks, changelog, status
- [ ] ADRs 0001–0011
- [ ] Fixtures: smdr, cm, syslog, sql, recordings
- [ ] `.agent/PLAN.md` `.agent/TODO.md` `.agent/project_config.json`
- [ ] README badges are Shields.io `style=flat-square` on `https://img.shields.io`

## Runtime

- [ ] `docker compose up --build` starts api + postgres + web
- [ ] `GET /api/health` returns 200 with `fixtures` flag
- [ ] `POST /api/ingest/fixtures` loads CDR, logs, dialplan, recordings meta
- [ ] `GET /api/cdr` filters, paginates, returns `raw_record` on detail
- [ ] `GET /api/export?format=csv` downloads
- [ ] `GET /api/pbx` and `/api/pbx/{id}/health` from mock
- [ ] `GET /api/dialplan` returns fixture ARS/IPO rows
- [ ] `GET /api/logs?kind=sip` and `kind=e1` return fixture lines
- [ ] Unencrypted `GET /api/recordings/{id}/audio` is 200 audio
- [ ] Encrypted IPO fixture audio is **409** with `reason=ipo_encrypted_r11`
- [ ] No SysMonitor client in the tree (`rg -i sysmonitor` only hits docs forbidding it)

## UI

- [ ] Four views route and render fixture CDR
- [ ] Health / Dialplan / Logs / Recordings pages exist
- [ ] Russian default strings; English toggle
- [ ] Encrypted recording shows explanation, not a broken `<audio>`

## Quality

- [ ] `pytest` green with `USE_FIXTURES=true` and no live hosts
- [ ] Frontend unit tests green
- [ ] ruff + mypy (backend) clean on the slice that introduced code
- [ ] Identifiers English; new comments Russian
- [ ] No `.env`, no customer audio, no real numbers

## Git

- [ ] Slice commits in natural Russian
- [ ] `main` pushed to `origin`
