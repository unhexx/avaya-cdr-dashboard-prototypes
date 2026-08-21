# ADR 0002 — Canonical CDR store

**Status:** Accepted  
**Date:** 2026-08-21

## Context

CDR arrives as heterogeneous text (CM unformatted/expanded/customized, IPO SMDR CSV). Operators still need the original line for disputes.

## Decision

PostgreSQL table `cdr_records` is the system of record. Every ingested line is normalized **and** stored as `raw_record` with `raw_hash` SHA-256 for idempotent ingest. UCID is indexed but **not** the unique key (unformatted streams often lack it).

MariaDB is **not** the canonical CDR store; it is only an optional recordings sql-source (ADR 0005).

## Consequences

- Export and UI always read Postgres.
- Re-parse is possible from `raw_record` after parser fixes (optional later job).
