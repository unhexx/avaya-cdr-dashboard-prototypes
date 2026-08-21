# INTEGRATION — AVAYA

Maximum compatibility in v1 means **parse what Avaya emits on documented channels**, not a full AES CTI stack.

## Platform matrix

| Product | Releases we care about | Channels in v1 | Out |
|---|---|---|---|
| Aura Communication Manager | 6.x–10.x CDR formats; SAT | IP-CDR TCP, SAT SSH, SNMP | Write SAT, unofficial CDR-over-RPC |
| IP Office | R10–R11.1+ SMDR CSV | SMDR TCP, SNMP, SSA HTTPS | **SysMonitor**, encrypted media decrypt |
| Session Manager | 7.x–10.x | syslog, SNMP | traceSM interactive, PPM write |
| SBCE | 8.x–10.x | syslog, SNMP | EMS write |
| Contact Recorder / VMPro DB | sidecar MariaDB/PG | sql-source read | Proprietary decrypt |

## Communication Manager CDR

Administered as **IP CDR** (printer over TCP) toward this app’s `CM_CDR_LISTEN_PORT` (default 9000).

Formats (`CM_CDR_FORMAT` or auto-detect):

| Format | Signature | Parser |
|---|---|---|
| Unformatted | space-padded columns, no date in some loads | `parsers.cdr_cm.parse_unformatted` |
| Expanded | includes date + UCID (18–20 digits typical) | `parsers.cdr_cm.parse_expanded` |
| Customized | delimiter from SAT `display system-parameters cdr` (often `&` or `\|`) | `parsers.cdr_cm.parse_customized` |

Condition codes are preserved in `condition_code`; mapped to `disposition` with a documented table in the parser (unknown → `other`). **Always keep `raw_record`.**

UCID when present is the join key to recordings and SIP `Call-ID` correlation is best-effort only.

## SAT allowlist (v1)

```
status health
display alarms
status trunk
status ds1
list measurements occupancy
list measurements ds1 summary
list ars analysis
display dialplan analysis
list station
list vdn
list hunt-group
status processor-channel
display system-parameters cdr
```

Anything else is **dropped** with a security log. No pager (`page`), no `change`.

## IP Office SMDR

Default TCP **8888**, CSV, one row per segment. `Continuation=1` → `is_transferred`. Column sets differ by release; parser is **header-based**, not positional.

Typical headers: `Call Start`, `Connected Time`, `Ring Time`, `Caller`, `Direction`, `Called Number`, `Dialled Number`, `Account`, `Is Internal`, `Call ID`, `Continuation`, `Party1Device`, `Party1Name`, `Party2Device`, `Hold Time`, `Park Time`, `Unique Call ID`.

Direction `I`/`O`/`L` → inbound / outbound / internal.

## IP Office — SysMonitor

**Forbidden.** SysMonitor’s session is an undocumented diagnostic protocol. We will not:

- speak its TCP/UDP framing
- replay captures
- ship a “SysMonitor-compatible” decoder

Health without it: SNMP (Avaya / standard HOST-RESOURCES), SSA HTTPS XML, SMDR presence, optional ICMP.

## Session Manager / SBCE

Syslog (RFC 5424 or BSD). SIP lines tagged `SIP:` / `INVITE` / `SIP/2.0`. Correlate on `Call-ID` when present. No custom SIP stack.

## E1 / T1 (DS1)

CM `status ds1` + syslog MEDPRO. Alarm tokens: `LOS` (red), `RAI` (yellow), `AIS` (blue), `SLIP`, `CRC`, `BPV`. Stored on `log_events` with `kind='e1'`.

## Recordings join

`recording_meta.ucid = cdr_records.ucid` when both exist; else `(start_time ± 2s, calling_number, dialed_number)` heuristic, flagged `extra.join = "heuristic"`.
