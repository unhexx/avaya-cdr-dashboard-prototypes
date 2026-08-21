# ADR 0006 — Fixtures, not a live PBX, for CI

**Status:** Accepted  
**Date:** 2026-08-21

## Context

Agents cannot assume CM/IPO on the LAN. Tests that need a real SAT will flake.

## Decision

Golden files live in `docs/fixtures/{cm,smdr,syslog,sql,recordings}`. Default `USE_FIXTURES=true`. Live connector tests are skipped unless `ENABLE_LIVE_CONNECTORS=true` (never on CI).

Every new parser ships a fixture in the same PR.

## Consequences

- First release is demonstrable with `POST /api/ingest/fixtures`.
- Format drift vs a customer’s customized CDR is handled by adding a fixture, not by SSHing to production from CI.
