# PRODUCT

## Persona

Primary: PBX operator / voice engineer for a single Avaya site (CM and/or IP Office, often with Session Manager and SBCE). Secondary: contact-center supervisor (VDN, agent, abandon). Tertiary: analyst exporting CDR.

## v1 jobs-to-be-done

1. **Is the PBX sick?** Alarms, trunk/DS1 state, occupancy snapshot, collector connectivity.
2. **What happened on this number?** CDR/SMDR search, raw line, related recording if any.
3. **Why did that number fail?** Dialplan / ARS row that matched; SIP 4xx/5xx and E1 alarms in the same window.
4. **Play that call.** On-demand audio from sql-source; if IPO encrypted ≥ R11.1, show why (409), do not pretend to play.

## Capabilities

| Area | v1 |
|---|---|
| CDR | Ingest CM IP-CDR + IPO SMDR; filter, sort, paginate, export CSV/JSON |
| Health | Node list, last snapshot, alarm feed (mock + SNMP/SAT when configured) |
| Dialplan | Searchable dump of ARS / dialplan analysis / IPO shortcodes |
| Logs | Syslog ingest; SIP and E1/DS1 views; time-bounded search |
| Recordings | List by UCID / time; play unencrypted; 409 for encrypted IPO |
| UI | Classic table, analytics, contact-center, modern cards; ru + en |

## Non-goals (v1)

- Full AES TSAPI event stream.
- Writing the PBX configuration.
- Multi-site tenancy.
- Decrypting Avaya media encryption.
- SysMonitor-level IPO internals.

## UX principles

- Desktop first; tablet usable; mobile for search and cards (prototype 4).
- Russian default. English via `?lang=en` / toggle, `localStorage`.
- Empty states explain **fixture mode** vs **live connector down**.
- Destructive actions: none in v1 (read-only ops).

## Success metrics (qualitative for v1)

- Operator finds a call by calling number in < 3 clicks.
- Health page shows collector + PBX state without a live box (fixtures).
- Encrypted recording is honest (409), not a broken player.
