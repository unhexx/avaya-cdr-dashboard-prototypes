# ADR 0008 — SIP/E1 via syslog, not pcap

**Status:** Accepted  
**Date:** 2026-08-21

## Context

SIP troubleshooting can mean tcpdump on SM/SBCE. Building a packet capture pipeline is a different product.

## Decision

Ingest **syslog** (and SAT DS1 text) only. Classify SIP vs E1 vs alarm with heuristics. No libpcap, no HEP/HEPv3, no custom SIP stack in v1.

## Consequences

- Operators must point SM/SBCE/CM syslog at the dashboard.
- We will miss packets that were never logged.
