# ADR 0005 — Recordings sql-source and encrypted IPO media

**Status:** Accepted  
**Date:** 2026-08-21

## Context

The product goal requires on-demand recordings via MariaDB/PostgreSQL sql-source. IP Office ≥ R11.1 typically encrypts VMPro/Media Manager recordings with platform keys we do not own.

## Decision

1. Metadata is **SELECTed** from a customer MariaDB or PostgreSQL (`RECORDINGS_SQL_URL`), mapped into `recording_meta`.
2. Audio bytes are read from `RECORDINGS_MEDIA_ROOT` + relative path. No path traversal.
3. If `encrypted` or `encryption_hint=ipo_r11` (or `.enc` suffix): **HTTP 409** on the audio route, metadata still listed.
4. `RECORDINGS_ALLOW_ENCRYPTED_AUDIO=false` is the only supported value in v1. No decryptor.

## Consequences

- Honest UX for encrypted calls.
- ACR-style SQL catalogs work without Avaya media APIs.
- We will not ship keys or unwrap AES.
