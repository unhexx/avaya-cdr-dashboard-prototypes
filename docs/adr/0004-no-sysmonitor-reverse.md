# ADR 0004 — Do not reverse SysMonitor

**Status:** Accepted  
**Date:** 2026-08-21

## Context

Avaya IP Office SysMonitor is the familiar Windows diagnostic tool. Its on-the-wire protocol is undocumented. Reverse-engineering it would improve IPO internals visibility but is legally and operationally out of bounds for this project.

## Decision

**No SysMonitor client, capture decoder, or “compatible” framing.** IPO health uses SNMP, SSA HTTPS (documented XML), SMDR TCP liveness, and optional ICMP. Documentation may mention SysMonitor only to forbid it.

## Consequences

- Some IPO trace views operators know from SysMonitor will not exist in v1.
- PRs adding `sysmonitor` protocol code are rejected.
