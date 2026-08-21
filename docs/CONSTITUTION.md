# CONSTITUTION

Laws. Agents do not vote them down in application code. Change requires a new ADR and an update here.

## I. Avaya interfaces

1. **Official only.** SAT/OSSI (SSH), CM IP-CDR TCP, IPO SMDR TCP, SNMP, SSA HTTPS, syslog, SQL-source, published REST where Avaya documents it.
2. **SysMonitor is off-limits.** No capture, no reimplementation, no "compatible client". Health for IP Office uses SNMP, SSA, SMDR, and (optionally) documented DevLink/TAPI — not SysMonitor (ADR 0004).
3. **SAT v1 is read-only.** Allowlist in `docs/INTEGRATION_AVAYA.md`. No `change`, `add`, `remove`, `busyout`, `release`, `reset`, `set time`.
4. **Maximum compatibility** means: parse the formats Avaya actually emits (CM unformatted / expanded / customized; IPO SMDR CSV across R10–R11+ column sets), not that we emulate every AES CTI event in v1.

## II. Recordings

5. Audio is **on-demand**. Metadata comes from a **MariaDB or PostgreSQL sql-source** plus optional `RECORDINGS_MEDIA_ROOT`.
6. **Encrypted IP Office media (typical ≥ R11.1)** is never decrypted. `GET /api/recordings/{id}/audio` returns **HTTP 409** with JSON metadata (`encrypted: true`, `reason: "ipo_encrypted_r11"`). No ffmpeg, no key extraction, no "try the VMPro password as AES".
7. Customer audio is not committed. Fixtures may include a tiny unencrypted placeholder WAV.

## III. Data and CI

8. **PostgreSQL** is the system of record. Raw CDR/SMDR lines are stored in `raw_record`.
9. **CI has no live PBX.** Parsers and connectors have a mock implementation fed by `docs/fixtures/**` (ADR 0006).
10. **Ambiguous forks become ADRs.** Do not ship two competing parsers or two auth systems.

## IV. Product and language

11. **Single-tenant v1.** Optional HTTP basic auth from env. No multi-tenant RLS.
12. **One SPA**, four call views plus Health / Dialplan / Logs / Recordings (ADR 0010).
13. Product documentation: **English**. Code identifiers: **English**. Comments and commit messages: **natural Russian** (ADR 0011).
14. README badges: **Shields.io only**, `style=flat-square`, public URLs on `https://img.shields.io`.
15. **No secrets in git.** `.env.example` is placeholders.

## V. Process

16. One INVEST slice per fire. Merge to `main` when tests are green.
17. v1 is done when `docs/ACCEPTANCE.md` is fully checked and `origin/main` has the green run.
