# TODO

## D0 Docs package

- [x] Root: AGENTS.md README.md LICENSE .gitignore .env.example Agent-Init.sh SYSTEM_PROMPT.md TASK_SPECIFICATION.md DEVELOPMENT_STANDARDS.md prompts/short_orchestrator_prompt.md
- [x] docs v2.0 index + CONSTITUTION PRODUCT ARCHITECTURE DATA_MODEL API CONNECTORS INTEGRATION_AVAYA DIALPLAN LOGS RECORDINGS UI_SPEC SECURITY TESTING DEPLOYMENT ACCEPTANCE ROADMAP AGENT_GUIDE TASKS CHANGELOG STATUS
- [x] ADRs 0001–0011
- [x] Fixtures smdr/cm/syslog/sql/recordings
- [x] .agent PLAN TODO project_config; SPRINTPLAN PROJECT_CONTEXT
- [ ] Push to origin/main (this fire)
- [ ] ACCEPTANCE docs checkboxes true on origin

## P0 Scaffold (next fire)

- [ ] backend FastAPI + settings + /api/health
- [ ] docker-compose.yml postgres + api
- [ ] Alembic migration for DATA_MODEL.md
- [ ] pytest skeleton

## P1 CDR ingest

- [ ] CM unformatted/expanded/customized parsers
- [ ] IPO SMDR parser
- [ ] GET /api/cdr + export
- [ ] ingest fixtures endpoint

## P2 Health

- [ ] snapshots + alarms + mock SAT
- [ ] /health UI

## P3 Dialplan

- [ ] ARS + IPO shortcode parse
- [ ] /dialplan UI

## P4 Logs

- [ ] syslog classifier SIP/E1
- [ ] /logs UI

## P5 Recordings

- [ ] sql-source adapter
- [ ] audio 200 / 409 ipo_encrypted_r11

## P6 UI four views

- [ ] classic / analytics / cc / cards + i18n

## P7 Harden

- [ ] CI compose smoke
- [ ] ACCEPTANCE v1 complete
