# API

Base path: `/api`. JSON, UTF-8. Errors: `{ "error": { "code": "...", "message": "..." } }`.

Auth: if `APP_BASIC_AUTH_USER` is non-empty, HTTP Basic; else open (dev/fixtures).

## Health

| Method | Path | Notes |
|---|---|---|
| GET | `/api/health` | Process liveness `{ status, version, fixtures }` |
| GET | `/api/pbx` | Node list |
| GET | `/api/pbx/{id}/health` | Last snapshot + open alarms |
| GET | `/api/alarms` | Query: `severity`, `open=true`, `from`, `to` |

## CDR

| Method | Path | Notes |
|---|---|---|
| GET | `/api/cdr` | See filters |
| GET | `/api/cdr/{id}` | Includes `raw_record` |
| GET | `/api/stats` | KPI for analytics view |
| GET | `/api/export` | `format=csv\|json` (xlsx optional) |

### GET /api/cdr filters

`from`, `to` (ISO-8601), `direction`, `disposition`, `calling_number`, `dialed_number` (`match=contains\|exact\|prefix`), `agent_extension`, `vdn`, `trunk`, `account_code`, `q` (full-text on numbers), `sort` (default `-start_time`), `page`, `page_size` (10/25/50/100/500).

Response:

```json
{
  "items": [],
  "page": 1,
  "page_size": 25,
  "total": 0,
  "summary": { "count": 0, "talk_seconds": 0 }
}
```

## Dialplan

| Method | Path |
|---|---|
| GET | `/api/dialplan?q=&source=` |
| POST | `/api/dialplan/sync` | Mock or SAT dump (no-op if live disabled)

## Logs

| Method | Path |
|---|---|
| GET | `/api/logs` | `kind=sip\|e1\|alarm`, `from`, `to`, `q`, `call_id` |

## Recordings

| Method | Path | Notes |
|---|---|---|
| GET | `/api/recordings` | Metadata list |
| GET | `/api/recordings/{id}` | Metadata |
| GET | `/api/recordings/{id}/audio` | `200` audio stream **or** `409` |

### 409 body (encrypted IPO)

```json
{
  "error": {
    "code": "recording_encrypted",
    "message": "IP Office recording is encrypted (R11.1+). Metadata only.",
    "reason": "ipo_encrypted_r11"
  },
  "recording": { "id": 1, "encrypted": true, "ucid": "..." }
}
```

Never 200 with garbage bytes.

## Ingest (ops / CI)

| Method | Path |
|---|---|
| POST | `/api/ingest/fixtures` | Load `docs/fixtures/**` (dev + CI) |
| POST | `/api/mock-generate?n=5000` | Synthetic CDR (prototype generator) |

## OpenAPI

FastAPI `/api/docs` (Swagger) and `/api/openapi.json`. Routers must declare response models; 409 is a documented status on the audio route.
