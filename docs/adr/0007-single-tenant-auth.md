# ADR 0007 — Single-tenant v1 authentication

**Status:** Accepted  
**Date:** 2026-08-21

## Context

v1.0 listed multi-tenancy as out of scope. Operators run one dashboard per site.

## Decision

Single tenant. Optional HTTP Basic via `APP_BASIC_AUTH_USER` / `APP_BASIC_AUTH_PASSWORD`. If unset, open API **bound to localhost** in compose. No SSO, no RBAC roles, no row-level tenant_id.

## Consequences

- Faster v1.
- Multi-site customers run multiple compose stacks or wait for a later ADR.
