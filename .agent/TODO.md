# TODO

## D0 Docs package

- [x] Root: AGENTS.md README.md LICENSE .gitignore .env.example Agent-Init.sh SYSTEM_PROMPT.md TASK_SPECIFICATION.md DEVELOPMENT_STANDARDS.md prompts/short_orchestrator_prompt.md
- [x] docs v2.0 index + CONSTITUTION PRODUCT ARCHITECTURE DATA_MODEL API CONNECTORS INTEGRATION_AVAYA DIALPLAN LOGS RECORDINGS UI_SPEC SECURITY TESTING DEPLOYMENT ACCEPTANCE ROADMAP AGENT_GUIDE TASKS CHANGELOG STATUS
- [x] ADRs 0001–0011
- [x] Fixtures smdr/cm/syslog/sql/recordings
- [x] .agent PLAN TODO project_config; SPRINTPLAN PROJECT_CONTEXT
- [x] Push to origin/main (this fire)
- [x] ACCEPTANCE docs checkboxes true on origin

## P0 Scaffold (this fire)

- [x] backend FastAPI + settings + /api/health
- [x] docker-compose.yml postgres + api
- [x] Alembic migration for DATA_MODEL.md
- [x] pytest skeleton

## P1 CDR ingest

- [x] CM unformatted/expanded/customized parsers
- [x] IPO SMDR parser
- [x] GET /api/cdr + export
- [x] ingest fixtures endpoint

## P2 Health (this fire)

- [x] snapshots + alarms + mock SAT
- [x] /health UI

## P3 Dialplan

- [ ] ARS + IPO shortcode parse
- [ ] /dialplan UI

## P4 Logs

- [ ] syslog classifier SIP/E1
- [ ] /logs UI

## P5 Recordings

- [x] sql-source adapter (fixtures; live SELECT stub → health degraded)
- [x] audio 200 / 409 ipo_encrypted_r11
- [ ] live MariaDB/PG SELECT for RECORDINGS_SQL_URL (сейчас sql_stub/degraded)

## P6 UI four views

- [x] classic / analytics / cc / cards + i18n

## P7 Harden

- [ ] CI compose smoke
- [ ] ACCEPTANCE v1 complete
