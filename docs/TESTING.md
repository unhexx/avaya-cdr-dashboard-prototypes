# TESTING

## Principle

Green CI **without a live PBX**. `ENABLE_LIVE_CONNECTORS` tests are skipped unless that env is true (never on GitHub Actions).

## Backend

```
pytest -q
```

| Layer | What |
|---|---|
| Parsers | Golden files in `docs/fixtures/cm`, `smdr`, `syslog` |
| Dedup | Same `raw_record` ingested twice → one row |
| API | Starlette `AsyncClient`, fixtures loaded via `/api/ingest/fixtures` |
| Recordings | Unencrypted 200 + `Content-Type`; encrypted 409 JSON |
| SAT allowlist | Reject `change system-parameters` |
| Health | Mock snapshot `status in {ok,degraded,down,unknown}` |

Coverage target: parsers 90%+, API 70%+.

## Frontend

```
cd frontend && npx vitest run
```

Filter store, disposition mapping, 409 player banner, i18n keys present in ru and en.

## Compose smoke

```
docker compose up --build -d
curl -sf localhost:8000/api/health
curl -sf -X POST localhost:8000/api/ingest/fixtures
curl -sf localhost:8000/api/cdr?page_size=10
```

## Forbidden tests

- Opening SysMonitor ports.
- Asserting plaintext audio for `encryption_hint=ipo_r11`.
- Hitting real customer IPs.

## Fixtures

See `docs/fixtures/README.md`. Adding a parser without a fixture fails review.
