# AGENT GUIDE

## Cold start

1. `bash Agent-Init.sh && source .venv/bin/activate`
2. Read `.agent/TODO.md`, `docs/STATUS.md`, `docs/TASKS.md`, `docs/ACCEPTANCE.md`
3. If docs package incomplete → write docs only
4. Else implement the next INVEST slice
5. Stop after one slice

## Definition of a slice

- Fits in one PR
- Has tests or a fixture
- Updates `docs/STATUS.md` + `.agent/TODO.md`
- Commit message in natural Russian

## Order (do not skip)

See `docs/TASKS.md`. Health before pretty charts is fine; parsers before API; API before UI wiring.

## Forks

If two designs appear, add `docs/adr/00NN-title.md`, lock one, implement that one.

## Avaya traps

- Do not scrape SysMonitor. If IPO health is weak, use SNMP/SSA/SMDR heartbeat.
- Do not “just ffmpeg” encrypted blobs.
- Do not send SAT commands built from search boxes.

## Workspace note

If the checkout under `/home/unhex/_PROJECT/avaya-cdr-dashboard-prototypes` is root-owned, clone or worktree into a user-writable path, commit, **push to origin/main**. The stop condition is origin, not the local uid.

## Status block (every fire)

```
phase: ...
branch: ...
HEAD: ...
files: ...
tests: pass|fail|n/a
next_slice: ...
stop_met: yes|no
blocker: ...
```
