# UI SPEC

One SPA (ADR 0010). Four call views from v1.0 prototypes plus ops pages. Russian default, English i18n.

**Brand:** Aquarius visual system is mandatory — see [`BRAND.md`](BRAND.md). Tokens: accent `#28AFCA`, base `#A2B7C8`, dark `#24566C`, Inter, pixel motif. Map Tailwind / CSS variables / shadcn to those HEX values only.

Shared chrome: top nav (existing `Header` with pixel mark), date-range (Today / Yesterday / Last 7 / 30 / This month / custom), theme toggle, language toggle. Filter state in Zustand + URL query.

## Prototype 1 — Classic table `/`

- Collapsible left **FilterPanel**: direction, disposition, calling/dialed (contains/exact/prefix), agent, VDN, account, trunk, duration min/max.
- Top: quick search, date range, export CSV/JSON, column visibility.
- **TanStack Table**, virtualized (`react-virtual`) at ≥ 1000 rows.
- Sticky header, row selection, bulk export, expand row → raw record + extra fields.
- Pagination 10/25/50/100/500. Summary: total records, filtered, talk seconds.
- Keyboard: `/` focuses search, `j`/`k` move, `Enter` opens detail.

Disposition colors: answered green, abandoned red, busy amber, other muted.

## Prototype 2 — Analytics `/analytics`

- KPI cards: Total, Answered, Abandoned %, Avg duration, Avg ring, Peak hour, Top calling number, Unique agents.
- Charts (Recharts): volume by hour, direction pie, daily trend area, top dialed/calling bar.
- Click chart slice → apply filter, stay in sync with the table store.
- Lower half: the same DataTable, filtered.

## Prototype 3 — Contact center `/cc`

- Filters: VDN, skill, agent group.
- SLA % (answered within X seconds, default 20; env `SLA_THRESHOLD_SECONDS`).
- Agent performance table: handled, avg handle, abandon rate.
- Heatmap hour × weekday.
- Queue/VDN summary cards with color thresholds (abandon > 8% red, wait > SLA amber).

## Prototype 4 — Modern cards `/cards`

- Search-first, facet chips.
- Card list compact/expanded.
- Timeline in drawer: ring → answer → hold → transfer → end.
- Table/cards toggle. Dark mode. WCAG 2.1 AA target.

## Ops pages

| Route | Content |
|---|---|
| `/health` | Node cards, status, occupancy sparkline, open alarms |
| `/dialplan` | Prefix search, source tabs, raw SAT/IPO |
| `/logs` | SIP / E1 / alarm tabs |
| `/recordings` | List, play (200) or encrypted banner (409) |

## Components (shared)

`DateRangePicker`, `FilterPanel`, `DataTable`, `ExportButton`, `ColumnVisibility`, `KpiCard`, `ThemeToggle`, `AudioPlayer`, `AlarmBadge`, `EmptyFixturesHint`.

## i18n

`frontend/src/i18n/{ru,en}.json`. No hardcoded English in user-visible React except brand “Avaya”.

## Accessibility

Focus rings, `aria-sort` on table headers, contrast in both themes. No information by color alone (disposition also has a letter/icon).
