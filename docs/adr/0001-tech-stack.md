# ADR 0001 — Tech stack

**Status:** Accepted  
**Date:** 2026-08-21

## Context

v1.0 prototype spec allowed FastAPI *or* NestJS. Frontend scaffold is already Vite + React 18 + TypeScript + Tailwind.

## Decision

**Backend: Python 3.12 + FastAPI + SQLAlchemy 2 + Alembic + Pydantic v2.**  
**Frontend: keep the existing React/Vite SPA.**  
**Canonical DB: PostgreSQL 16.**  
**Recordings sql-source: MariaDB or PostgreSQL (read-only).**

Reject NestJS / Prisma as the v1 backend to avoid two languages in connectors (SAT text, CDR parsers, SNMP) and to match sibling agent repos.

## Consequences

- Parsers are plain Python, easy to fixture-test.
- Frontend remains TypeScript.
- Agents must not add a second API framework without a new ADR.
