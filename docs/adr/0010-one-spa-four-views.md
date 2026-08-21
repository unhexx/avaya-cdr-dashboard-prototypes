# ADR 0010 — One SPA, four call views plus ops pages

**Status:** Accepted  
**Date:** 2026-08-21

## Context

v1.0 asked for four independent prototypes. A production dashboard with health/logs/recordings cannot be four apps.

## Decision

**One Vite SPA.** Routes `/`, `/analytics`, `/cc`, `/cards` implement the four prototypes as views sharing Zustand filters and the same API. Additional routes: `/health`, `/dialplan`, `/logs`, `/recordings`. Shared components live in `frontend/src/components`.

## Consequences

- Prototype “independence” is visual, not deployment.
- Filter chips on analytics apply to the classic table store.
