# Fixtures

Golden files for parsers and `POST /api/ingest/fixtures`. **No real customer numbers.** Fake MSISDNs use `7903*` / `8495*`; extensions `12xx`; UCID `00001001234567890123` style.

| Directory | Parser |
|---|---|
| `cm/` | CM IP-CDR unformatted / expanded / customized + `cm/sat/` SAT text |
| `smdr/` | IPO SMDR CSV |
| `syslog/` | SIP and E1/DS1 syslog |
| `sql/` | recording_meta catalog (JSON + MariaDB-dialect SQL) |
| `recordings/` | tiny unencrypted WAV; encrypted is **metadata only** |

Do not add SysMonitor captures.
