# SECURITY

## Secrets

- `.env` gitignored. `.env.example` empty placeholders.
- No customer numbers in fixtures (use the documented fake prefixes `7903…` / `8495…` / extensions `12xx`).
- No real audio. No SAT host keys in git.

## Auth (v1)

Single-tenant (ADR 0007). Optional HTTP Basic from `APP_BASIC_AUTH_*`. If unset, API is open — **compose binds `127.0.0.1` by default** in `DEPLOYMENT.md`.

No JWT, no SSO in v1.

## SAT

- Read-only allowlist. User input never concatenated into a SAT command.
- SSH password/key from env. Optional fingerprint pin `CM_SAT_HOSTKEY`.
- Session timeout `CM_SAT_TIMEOUT_SECONDS`.

## sql-source

Read-only DB user. SELECT-only. Path join rejects `..` and absolute paths outside `RECORDINGS_MEDIA_ROOT`.

## Recordings

Encrypted IPO media: 409, no decrypt. Serving audio uses `Content-Type` from mime map, `Cache-Control: private`.

## SysMonitor

Not implemented. Attempts to add it fail code review (constitution I.2).

## Logging

No passwords, community strings, or full `.env` dumps. CDR numbers are operational data — do not print entire `raw_record` at INFO in production (`DEBUG` only).

## Supply chain

Pin Docker images by digest when tagging v1. Python deps via lockfile (`uv.lock` or `requirements.txt` hash). npm `package-lock.json`.
