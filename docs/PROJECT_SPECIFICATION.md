# PROJECT SPECIFICATION — Avaya CDR Dashboard

**Version:** 2.0.0  
**Date:** 2026-08-21  
**Repository:** https://github.com/unhexx/avaya-cdr-dashboard-prototypes  
**Status:** Index (supersedes v1.0 prototype-only specification)

This file is the **map**. Normative detail lives in the documents below. If a later doc conflicts with v1.0 text, the later doc and the ADRs win.

v1.0 described four UI prototypes and a CDR canonical model. v2.0 keeps those views and that model, and adds the first-release product: PBX health, dialplan, SIP/E1 logs, recordings sql-source, and Avaya connector law.

---

## 1. Index

| Doc | Role |
|---|---|
| [CONSTITUTION.md](CONSTITUTION.md) | Non-negotiable laws |
| [PRODUCT.md](PRODUCT.md) | What v1 ships |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Components, data flow |
| [DATA_MODEL.md](DATA_MODEL.md) | PostgreSQL canonical schema |
| [API.md](API.md) | HTTP/JSON contract |
| [CONNECTORS.md](CONNECTORS.md) | Plugin pack |
| [INTEGRATION_AVAYA.md](INTEGRATION_AVAYA.md) | Platform matrix (CM, IPO, SM, SBCE) |
| [DIALPLAN.md](DIALPLAN.md) | ARS / IPO dial-plan ingest |
| [LOGS.md](LOGS.md) | SIP / E1 / syslog |
| [RECORDINGS.md](RECORDINGS.md) | sql-source + 409 rule |
| [UI_SPEC.md](UI_SPEC.md) | Four views + ops pages (from v1.0) |
| [SECURITY.md](SECURITY.md) | Auth, secrets, SAT allowlist |
| [TESTING.md](TESTING.md) | Fixtures, pytest, CI |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Docker Compose |
| [ACCEPTANCE.md](ACCEPTANCE.md) | Definition of Done v1 |
| [ROADMAP.md](ROADMAP.md) | Phases after v1 |
| [AGENT_GUIDE.md](AGENT_GUIDE.md) | How agents work this repo |
| [TASKS.md](TASKS.md) | INVEST backlog |
| [CHANGELOG.md](CHANGELOG.md) | History |
| [STATUS.md](STATUS.md) | Living status |
| [adr/](adr/) | ADR 0001–0011 (locked forks) |
| [fixtures/](fixtures/) | SMDR, CM CDR, syslog, SQL, recordings |

Root companions: `../AGENTS.md`, `../TASK_SPECIFICATION.md`, `../DEVELOPMENT_STANDARDS.md`, `../SYSTEM_PROMPT.md`, `../README.md`.

---

## 2. Product one-liner

A single-tenant operations SPA + FastAPI backend that ingests Avaya CDR/SMDR, shows PBX health, dialplan and SIP/E1 logs, and plays **on-demand** recordings resolved through a MariaDB or PostgreSQL sql-source — all testable from fixtures, without reversing SysMonitor, and without decrypting IPO ≥ R11.1 media.

---

## 3. v1.0 carry-forward

From the prototype spec, v2.0 **keeps**:

- Canonical CDR row (UCID, direction, disposition, durations, VDN, agent, trunks, `raw_record`).
- Four UI prototypes as **views** of one SPA (ADR 0010), not four apps.
- Filter / sort / export / column visibility / sticky header / virtualization.
- Mock generator ≥ 5 000 realistic rows for local demos.

v1.0 **out of scope** items that v2.0 **pulls in**: real TCP ingest (with mock fallback), call recording (sql-source only), health, dialplan, SIP/E1 logs.

---

## 4. Locked decisions

See [adr/](adr/). Short form:

1. FastAPI + React, PostgreSQL canonical.
2. Connector plugins, official protocols only.
3. No SysMonitor reverse.
4. Encrypted IPO recordings → 409 meta-only.
5. CI on fixtures.
6. Single-tenant v1.
7. Russian comments/commits; English identifiers and product docs.
