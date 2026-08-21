# ADR 0003 — Connector plugins

**Status:** Accepted  
**Date:** 2026-08-21

## Context

CM, IPO, SM, SBCE, SNMP, syslog, and SQL recordings all speak different protocols. A monolith of sockets inside route handlers will not test cleanly.

## Decision

`ProtocolConnector` ABC under `backend/app/connectors/`. Parsers are pure functions. Mock connector is first-class. Live connectors idle when hosts are empty.

**IPO SMDR:** dashboard is a **TCP client** to the IPO SMDR server (default port 8888).  
**CM IP-CDR:** dashboard is a **TCP server** (printer).  
**Syslog:** dashboard is a **UDP/TCP server**.

## Consequences

- CI never opens real PBX ports.
- New vendors require a connector + fixture + (if protocol is new) an ADR.
