# LOGS (SIP / E1 / syslog)

## Ingest

- UDP/TCP listen `SYSLOG_LISTEN_PORT` (default 5514).
- File drop: `docs/fixtures/syslog/*.log` via mock connector.
- No pcap reverse, no custom Ethernet tap (ADR 0008).

## Classification

| kind | Heuristics |
|---|---|
| `sip` | `INVITE`, `SIP/2.0`, `CSeq:`, `Call-ID:`, `traceSM`, `SBCE` SIP |
| `e1` | `DS1`, `LOS`, `RAI`, `AIS`, `SLIP`, `MEDPRO`, `board 0` |
| `alarm` | CM alarm log lines, SBCE `ALARM` |
| `other` | remainder, still stored |

## Retention

v1: all logs kept (operator’s DB). Index on `event_time DESC`. No auto-purge in v1; document a 30-day `DELETE` snippet in `DEPLOYMENT.md`.

## UI

`/logs` — kind tabs, time range (shared date picker), `q` on `message`, `call_id`. Click SIP `Call-ID` → CDR search `q=`.

## Privacy

Syslog may contain PII (PAI, From). Treat like CDR: no fixtures with real customer numbers; mask in screenshots.
