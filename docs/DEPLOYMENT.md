# DEPLOYMENT

## Compose (v1)

Services: `api`, `web`, `postgres`. Profiles:

- default: api + web + postgres  
- `recordings`: + `mariadb` loaded with `docs/fixtures/sql`  
- `redis`: optional cache  

Bind `127.0.0.1:8000` (API) and `127.0.0.1:4173` (web) unless `PUBLISH_PUBLIC=1`.

## Environment

Copy `.env.example` → `.env`. Minimum for fixture mode:

```
USE_FIXTURES=true
ENABLE_LIVE_CONNECTORS=false
DATABASE_URL=postgresql+asyncpg://avaya:avaya@postgres:5432/avaya_cdr
```

## Migrations

Alembic on API startup (`alembic upgrade head`) and as a compose `api` command prefix.

## SAT / SMDR on the LAN

- CM IP-CDR: administer printer to `dashboard:9000`.
- IPO SMDR: IP Office Manager → SMDR → IP address of dashboard, port 8888; dashboard **connects out** or listens — lock in connector code as **client to IPO** (ADR 0003 note: IPO is the server).
- Syslog: point SM/SBCE to `dashboard:5514`.
- Do not publish 5022/8888/5514 on a public interface.

## Backup

`pg_dump` the canonical DB. sql-source (recordings) is customer-owned — we do not dump it.

## Log purge (optional)

```sql
DELETE FROM log_events WHERE event_time < NOW() - INTERVAL '30 days';
```

## Health

`GET /api/health` for compose `healthcheck`. Postgres `pg_isready`.
