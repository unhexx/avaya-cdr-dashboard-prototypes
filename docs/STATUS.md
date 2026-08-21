# STATUS

**Phase:** P7 Harden  
**Branch target:** `execute-plan/bbe44169-pr-6-p7-harden-auth-ci-and-acceptance`  
**Stop-met:** yes (ACCEPTANCE v1 boxes honest; CI + optional basic auth)

## Last fire

P7: optional HTTP Basic (`APP_BASIC_AUTH_USER` gates API; open when unset) + `backend/tests/test_auth.py`; SAT allowlist / no-SysMonitor stay green; `.github/workflows/ci.yml` (pytest + ruff + mypy + frontend build, `USE_FIXTURES=true`, optional `compose config`); `docs/ACCEPTANCE.md` updated honestly; mypy fixes (dialplan loop vars, conftest Iterator).

## Next slice

Live `RECORDINGS_SQL_URL` SELECT (сейчас sql_stub/degraded) or Vitest for frontend — вне v1 STOP.

## Blockers

- Primary worktree may be root-owned; SSOT is `origin/main`.
- No SysMonitor. Encrypted IPO audio stays 409 (P5).
- P5 on-demand recordings: fixtures path live; `RECORDINGS_SQL_URL` without SELECT → connector health `degraded`/`sql_stub` (live engine deferred).
