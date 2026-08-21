# TASK_SPECIFICATION.md — Avaya CDR Dashboard

**Project:** Avaya CDR Dashboard (repo: `avaya-cdr-dashboard-prototypes`)  
**Version Target:** 1.0.0 first release (this cycle delivers the docs package as 0.2.0)  
**Primary Goal:** Autonomous first release of an operations dashboard with maximum Avaya compatibility: PBX health, CDR + SMDR, dialplan, SIP/E1 logs, on-demand recordings via MariaDB/PostgreSQL sql-source. No human in the loop.

## Business Objectives

- Give PBX operators one place to see **health**, **calls**, **dialplan**, **SIP/E1 logs**, and **recordings**.
- Ingest Communication Manager IP-CDR (unformatted / expanded / customized) and IP Office SMDR CSV without a live box in CI.
- Surface recordings stored in a customer MariaDB or PostgreSQL (Avaya Contact Recorder, VMPro sidecar, or equivalent). Encrypted IPO ≥ R11.1 media is listed, never decrypted (HTTP 409).
- Ship four UI views (classic table, analytics, contact-center, modern cards) plus Health / Dialplan / Logs / Recordings.
- Keep the product implementable by coding agents: INVEST slices, fixtures, ADRs, acceptance tests.

## Scope

**In scope (v1):**

- Docs package (this fire and any remaining doc gaps).
- FastAPI backend + PostgreSQL canonical store + Docker Compose.
- Connector pack: mock (always), CM IP-CDR TCP, IPO SMDR TCP, SAT SSH read-only, SNMP read, syslog UDP/TCP, recordings sql-source.
- Parsers for CM unformatted/expanded/customized and IPO SMDR CSV, golden fixtures under `docs/fixtures/`.
- REST API per `docs/API.md`.
- Vite SPA: four prototype views + health/dialplan/logs/recordings.
- Export CDR CSV/JSON (Excel xlsx optional).
- Russian UI, English i18n keys.

**Out of scope (v1):**

- Reverse-engineering SysMonitor or any undocumented diagnostic protocol.
- Decrypting IP Office ≥ R11.1 encrypted recordings.
- SAT write commands (`change`, `add`, `remove`, `busyout`, `release`).
- Multi-tenancy, SSO/SAML, full AES TSAPI/DMCC CTI, real-time media sniffing.
- Hosted SaaS, public-internet exposure of SAT/SMDR ports.

## Success Criteria

- `docs/ACCEPTANCE.md` all v1 boxes green.
- `pytest` and frontend unit tests pass on fixtures only (`USE_FIXTURES=true`).
- `docker compose up --build` brings API + Postgres + frontend.
- Encrypted recording audio endpoint returns **409** with metadata JSON.
- No SysMonitor client exists in the tree.
- No secrets, customer CDR, or real audio in git.
- Product docs English; commits and comments natural Russian; identifiers English.

## Delivery method

Agents execute `.agent/TODO.md` one INVEST item per fire, merge to `main`, push. Ambiguous forks become ADRs `docs/adr/0001`–`0011` (locked).
