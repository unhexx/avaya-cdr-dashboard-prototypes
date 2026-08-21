# ADR 0009 — Dialplan is a periodic dump

**Status:** Accepted  
**Date:** 2026-08-21

## Context

CM ARS can be watched via SAT. Real-time digit analysis needs CTI.

## Decision

Poll SAT allowlisted `list ars analysis` / `display dialplan analysis` (and IPO shortcode/ARS dumps) on an interval. Store rows in `dialplan_entries`. Search is longest-prefix match. No per-call live ARS trace in v1.

## Consequences

- Stale until next poll (default 15 minutes, or `POST /api/dialplan/sync`).
- Safe: no user-controlled SAT strings.
