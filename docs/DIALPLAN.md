# DIALPLAN

v1 is a **searchable dump**, not a live digit-by-digit analyzer (ADR 0009). Refresh: `POST /api/dialplan/sync` or SAT/IPO poller interval (default 15 min).

## Sources

| source | Origin | Fields used |
|---|---|---|
| `ars` | CM `list ars analysis` | prefix, min/max, route-pattern |
| `dialplan_analysis` | CM `display dialplan analysis` | percent-len, first-digit-type |
| `ipo_shortcode` | IPO SSA or fixture | short-code, telephone-number, feature |
| `ipo_ars` | IPO ARS table dump | prefix, dest |

## Operator flow

1. Paste a number in Dialplan search.
2. Longest-prefix match against `match_prefix`.
3. Show matching rows + `raw`.
4. Optional: CDR samples for that prefix in the last 24h (link, not inline join in SQL).

## Fixture

`docs/fixtures/cm/sat/list_ars_analysis.txt` and `docs/fixtures/cm/sat/display_dialplan_analysis.txt` plus IPO shortcode CSV.

## Parsing notes

SAT output is column-aligned text with form-feeds. Parser strips headers/footers (`Command:` / `press ESC`). Never send SAT the original command string built from user input — only constants from the allowlist, plus a validated numeric location if needed.
