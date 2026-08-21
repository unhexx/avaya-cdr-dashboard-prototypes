# DEVELOPMENT STANDARDS

Non-negotiable standards for every slice of Avaya CDR Dashboard. Applies to humans and coding agents.

---

## 1. Language (strict)

| Surface | Language |
|---|---|
| Product documentation (`README.md`, `AGENTS.md`, everything under `docs/` except quotes of Russian UI copy) | English |
| Git commit messages | Natural Russian, mid/senior developer voice |
| Code comments, docstrings, module notes | Natural Russian |
| Identifiers (modules, classes, functions, columns, JSON keys, CLI flags) | English |
| UI strings | Russian primary, English via i18n |

Forbidden in commits and comments: model names, "as an AI", "agent implemented", "this function does the following".

---

## 2. Quality bar

- Production-grade: typed, logged, error-handled, tested.
- No stubs that block the next slice.
- Small INVEST slices. One connector or one view per PR when possible.
- Every meaningful change is committed before the next slice.
- UTF-8 everywhere. Python `open(..., encoding="utf-8")`.

---

## 3. Avaya boundaries (see `docs/CONSTITUTION.md`)

- Official interfaces only: SAT/OSSI (read-only allowlist), SMDR TCP, CM IP-CDR TCP, SNMP, SSA HTTPS, syslog, SQL-source.
- **Never reverse-engineer SysMonitor** or any undocumented binary diagnostic protocol.
- Encrypted IP Office recordings (typical ≥ R11.1) → HTTP **409** + metadata. No key extraction, no brute-force, no "try ffmpeg".
- CI must pass on fixtures. A live PBX is optional and never required for green tests.
- Ambiguous forks → write an ADR and lock one option. Do not leave two implementations.

---

## 4. Environment

- Python only inside project `.venv` (`bash Agent-Init.sh` then `source .venv/bin/activate`).
- Prefer `uv`. Fallback: `python3 -m venv`.
- Configuration via environment / Pydantic Settings. Never hard-code secrets, customer numbers, or production hostnames.
- `.env` is gitignored. `.env.example` contains empty placeholders only.

---

## 5. Testing

- Unit tests for parsers against `docs/fixtures/**`.
- API tests with the mock connector pack.
- No test may open a real SAT/SMDR/SNMP session unless `ENABLE_LIVE_CONNECTORS=true` (opt-in, skipped in CI).
- Recording audio tests use the unencrypted placeholder only.

---

## 6. Git

- Branch from `main`. Slice branch names: `slice/<id>-<slug>` (English slug).
- Commit subject: natural Russian, imperative or past, ≤ 72 chars.
- Body: what and why, not how the model felt about it.
- Push the slice when tests are green. Merge to `main` only when `docs/ACCEPTANCE.md` for that slice is met.

---

## 7. Reviewer checks

Reject the slice if any of these fail:

- English identifiers mixed with transliterated Russian (`zvonok_id` → `call_id`).
- English comments on new Python/TS.
- SysMonitor protocol work, encrypted-blob decryptors, or committed `.env`.
- Missing fixture coverage for a new parser.
- README badges that are not Shields.io `style=flat-square`.
