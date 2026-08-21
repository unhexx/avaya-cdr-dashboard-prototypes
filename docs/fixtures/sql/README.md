# SQL recordings fixtures

`recordings.json` is the mock-connector source of truth. `recordings.sql` is the same catalog in MariaDB-ish DDL for the optional compose profile `recordings`.

Mapping to `recording_meta` is in `docs/RECORDINGS.md`. Encrypted rows must yield HTTP 409 on `/audio`.
