# Avaya CDR Dashboard

![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Python](https://img.shields.io/badge/python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/react-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/typescript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![MariaDB](https://img.shields.io/badge/MariaDB-sql--source-003545?style=flat-square&logo=mariadb&logoColor=white)
![Docker](https://img.shields.io/badge/docker-compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Avaya](https://img.shields.io/badge/Avaya-CM_%7C_IPO_%7C_SM_%7C_SBCE-E11F26?style=flat-square)
![UI](https://img.shields.io/badge/UI-Aquarius-28AFCA?style=flat-square)

Operations dashboard for Avaya voice platforms: **PBX health**, **CDR / SMDR**, **dialplan**, **SIP / E1 logs**, and **on-demand recordings** from a MariaDB or PostgreSQL sql-source.

First release targets maximum compatibility with Communication Manager, IP Office, Session Manager and SBCE using **official interfaces only**. Encrypted IP Office recordings (typical ≥ R11.1) are metadata-only (HTTP 409). CI runs on fixtures — a live PBX is not required.

The SPA uses the **Aquarius** visual system (azure `#28AFCA`, steel `#A2B7C8`, forest `#24566C`, Inter, pixel motif). Brand tokens: [`docs/BRAND.md`](docs/BRAND.md). UI language defaults to Russian.

## Spec index

**[`docs/PROJECT_SPECIFICATION.md`](docs/PROJECT_SPECIFICATION.md)** (v2.0) is the map. Laws: [`docs/CONSTITUTION.md`](docs/CONSTITUTION.md). Agent loop: [`AGENTS.md`](AGENTS.md). Status: [`docs/STATUS.md`](docs/STATUS.md).

## Quick start

```bash
bash Agent-Init.sh
source .venv/bin/activate
cp .env.example .env
docker compose up --build   # after the P0 scaffold slice
```

Frontend (already scaffolded):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Compatibility (v1)

| Platform | What we consume | What we do not |
|---|---|---|
| Communication Manager | IP-CDR TCP (unformatted / expanded / customized), SAT SSH read-only, SNMP | Write SAT, unofficial traces |
| IP Office | SMDR TCP CSV, SNMP, SSA HTTPS | **SysMonitor protocol** |
| Session Manager / SBCE | syslog, SNMP | Reverse-engineered SIP stacks |
| Recordings | SQL-source (MariaDB / PostgreSQL) + optional file root | Decrypt IPO ≥ R11.1 media |

## License

MIT. See [LICENSE](LICENSE).
