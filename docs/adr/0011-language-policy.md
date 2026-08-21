# ADR 0011 — Language policy

**Status:** Accepted  
**Date:** 2026-08-21

## Context

Host and sibling projects require natural Russian in commits/comments and English product docs. UI is for Russian operators.

## Decision

| Surface | Language |
|---|---|
| `docs/**`, README, AGENTS, ADRs | English |
| Identifiers, JSON keys, CLI, SQL names | English |
| Git commits, code comments, docstrings | Natural Russian |
| UI copy | Russian default, English i18n |

README badges: Shields.io only, `style=flat-square`, `https://img.shields.io`.

## Consequences

- Reviewer rejects `zvonok_id`, English comments on new Python, or model names in commits.
