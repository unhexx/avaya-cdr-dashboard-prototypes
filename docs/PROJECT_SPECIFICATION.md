# Полная спецификация проекта: Avaya CDR Dashboard Prototypes

**Версия:** 1.0.0  
**Дата:** 2026-08-21  
**Репозиторий:** https://github.com/unhexx/avaya-cdr-dashboard-prototypes  
**Назначение документа:** Полная, самодостаточная документация для автономной реализации проекта командой AI-агентов (Agent Club) **без участия человека**.  
**Язык реализации:** Русский (UI) + английский (код, комментарии, переменные).  
**Статус:** Готово к реализации.

---

## 1. Обзор проекта (Project Overview)

### 1.1. Видение
Создать современный веб-дашборд для анализа Call Detail Records (CDR) / Station Message Detail Recording (SMDR) от систем Avaya (Communication Manager, IP Office и совместимых). Система должна предоставлять **4 различных UI-прототипа**, ориентированных на фильтрацию и полный табличный просмотр записей звонков, с возможностью дальнейшего развития в production-ready решение.

### 1.2. Текущее состояние репозитория
Репозиторий содержит только `README.md` с описанием:
> Four UI prototypes for Avaya CDR call dashboard with filtering and full table view

Код, прототипы и документация отсутствуют. Данный документ является единственным источником истины для реализации.

### 1.3. Цели
1. Создать 4 независимых, но стилистически согласованных UI-прототипа дашборда CDR.
2. Обеспечить мощную систему фильтрации, поиска, сортировки и экспорта.
3. Предоставить полный табличный просмотр записей.
4. Заложить архитектуру, позволяющую легко подключить реальный парсер Avaya CDR (fixed-length / CSV SMDR) и базу данных.
5. Сделать систему полностью реализуемой автономными агентами.

### 1.4. Вне скоупа (Out of Scope) на этапе прототипов
- Реальная интеграция с Avaya CM/IP Office через TCP/serial/SSH (только mock + парсер форматов).
- Полноценная система аутентификации и multi-tenancy (можно добавить как опциональный слой).
- Запись звонков (call recording).
- Real-time streaming (симуляция допустима).

---

## 2. Целевая аудитория и сценарии использования

| Роль | Основные задачи | Какой прототип предпочтителен |
|------|-----------------|-------------------------------|
| Оператор / Аналитик | Поиск конкретных звонков, экспорт, детальный анализ | Prototype 1 (Classic Table) |
| Руководитель / BI | KPI, тренды, топ-номера, пиковые часы | Prototype 2 (Analytics) |
| Супервизор КЦ | VDN, агенты, SLA, abandoned | Prototype 3 (Contact Center) |
| Современный пользователь / Mobile | Быстрый поиск, карточки, timeline | Prototype 4 (Modern Cards) |

---

## 3. Модель данных CDR (Canonical Data Model)

### 3.1. Нормализованная схема (рекомендуется PostgreSQL)

```sql
CREATE TYPE call_direction AS ENUM ('inbound', 'outbound', 'internal', 'tandem', 'unknown');
CREATE TYPE call_disposition AS ENUM (
  'answered', 'abandoned', 'busy', 'no_answer', 'failed', 
  'transferred', 'conferenced', 'other'
);

CREATE TABLE cdr_records (
  id                    BIGSERIAL PRIMARY KEY,
  ucid                  VARCHAR(32) UNIQUE,               -- Unique Call ID (Avaya UCID)
  call_id               VARCHAR(32),                      -- Sequential / system call id
  start_time            TIMESTAMPTZ NOT NULL,
  answer_time           TIMESTAMPTZ,
  end_time              TIMESTAMPTZ,
  duration_seconds      INTEGER NOT NULL DEFAULT 0,      -- Connected time
  ring_duration_seconds INTEGER NOT NULL DEFAULT 0,
  hold_duration_seconds INTEGER DEFAULT 0,
  park_duration_seconds INTEGER DEFAULT 0,
  total_duration_seconds INTEGER GENERATED ALWAYS AS (
    duration_seconds + ring_duration_seconds + COALESCE(hold_duration_seconds,0) + COALESCE(park_duration_seconds,0)
  ) STORED,

  calling_number        VARCHAR(32),
  dialed_number         VARCHAR(64),
  connected_number      VARCHAR(64),                      -- final connected party
  direction             call_direction NOT NULL DEFAULT 'unknown',
  disposition           call_disposition NOT NULL DEFAULT 'other',

  -- Avaya-specific
  condition_code        VARCHAR(8),                       -- original condition code
  access_code_dialed    VARCHAR(8),
  access_code_used      VARCHAR(8),
  trunk_in              VARCHAR(16),
  trunk_out             VARCHAR(16),
  account_code          VARCHAR(32),
  auth_code             VARCHAR(16),
  attendant_console     VARCHAR(8),
  node_number           VARCHAR(8),
  vdn                   VARCHAR(16),                      -- Vector Directory Number
  agent_extension       VARCHAR(16),
  agent_id              VARCHAR(16),
  skill_group           VARCHAR(16),

  -- Meta
  is_internal           BOOLEAN DEFAULT FALSE,
  is_transferred        BOOLEAN DEFAULT FALSE,
  is_conferenced        BOOLEAN DEFAULT FALSE,
  source_system         VARCHAR(64) DEFAULT 'mock',       -- 'avaya-cm', 'ip-office', 'mock'
  raw_record            TEXT,                             -- original line for audit
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Индексы (критично для производительности)
CREATE INDEX idx_cdr_start_time ON cdr_records (start_time DESC);
CREATE INDEX idx_cdr_calling ON cdr_records (calling_number);
CREATE INDEX idx_cdr_dialed ON cdr_records (dialed_number);
CREATE INDEX idx_cdr_direction ON cdr_records (direction);
CREATE INDEX idx_cdr_disposition ON cdr_records (disposition);
CREATE INDEX idx_cdr_vdn ON cdr_records (vdn);
CREATE INDEX idx_cdr_agent ON cdr_records (agent_extension);
CREATE INDEX idx_cdr_account ON cdr_records (account_code);
CREATE INDEX idx_cdr_composite ON cdr_records (start_time, direction, disposition);
```

### 3.2. JSON Schema (для API и mock)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["start_time", "duration_seconds", "direction"],
  "properties": {
    "id": { "type": "integer" },
    "ucid": { "type": "string", "maxLength": 32 },
    "start_time": { "type": "string", "format": "date-time" },
    "duration_seconds": { "type": "integer", "minimum": 0 },
    "ring_duration_seconds": { "type": "integer", "minimum": 0 },
    "calling_number": { "type": "string" },
    "dialed_number": { "type": "string" },
    "direction": { "enum": ["inbound", "outbound", "internal", "tandem", "unknown"] },
    "disposition": { "enum": ["answered", "abandoned", "busy", "no_answer", "failed", "transferred", "conferenced", "other"] },
    "vdn": { "type": "string" },
    "agent_extension": { "type": "string" },
    "account_code": { "type": "string" },
    "trunk_in": { "type": "string" },
    "trunk_out": { "type": "string" }
  }
}
```

### 3.3. Источники данных (приоритет)
1. Mock data generator (обязателен на этапе прототипов).
2. Парсер fixed-length форматов Avaya CM (Unformatted, Expanded, Customized).
3. Парсер CSV SMDR Avaya IP Office.
4. В будущем: прямой TCP-приёмник CDR.

---

## 4. Функциональные требования

### 4.1. Общие для всех прототипов
- Фильтрация по:
  - Диапазону дат/времени (Date Range Picker + relative: Today, Yesterday, Last 7/30 days, This month)
  - Направлению (inbound / outbound / internal)
  - Disposition / статусу звонка
  - Calling Number / Dialed Number (частичное совпадение, exact, starts with)
  - Agent / Extension / VDN
  - Account Code
  - Минимальной / максимальной длительности
  - Trunk
- Полнотекстовый поиск по номерам и account code
- Сортировка по любой колонке
- Пагинация (10 / 25 / 50 / 100 / 500)
- Экспорт: CSV, JSON, Excel (xlsx)
- Сохранение набора фильтров (localStorage / URL query params)
- Responsive design (desktop first, tablet/mobile support)
- Светлая / тёмная тема
- i18n: русский (основной) + английский

### 4.2. Полный табличный просмотр
- Все ключевые поля
- Возможность показывать/скрывать колонки
- Sticky header
- Row selection + bulk actions (export selected)
- Expandable row details (raw record + дополнительные поля)

---

## 5. Четыре UI-прототипа (детальное описание)

### Prototype 1: Classic Advanced Table
**Цель:** Максимально эффективная работа с большими объёмами данных.

**Layout:**
- Левая боковая панель (collapsible) — Advanced Filters
- Верхняя панель — Quick search + Date range + Export + Column visibility
- Основная область — Dense Data Table (TanStack Table)
- Нижняя — Pagination + Summary (total records, filtered, avg duration)

**Ключевые особенности:**
- Multi-column filter (как в Excel)
- Column resizing + reordering
- Virtualized scrolling при > 1000 строк
- Keyboard navigation
- Цветовая индикация disposition (зелёный answered, красный abandoned и т.д.)

### Prototype 2: Analytics Dashboard
**Цель:** Быстрый обзор + drill-down.

**Layout:**
- Верхний ряд KPI-карточек (6–8 шт.):
  - Total Calls
  - Answered / Abandoned rate
  - Avg Duration / Avg Ring Time
  - Peak Hour
  - Top Calling Number
  - Unique Agents
- Средний ряд: Charts (Recharts)
  - Volume by Hour (bar/line)
  - Direction distribution (pie/donut)
  - Daily trend (area)
  - Top 10 Dialed / Calling (horizontal bar)
- Нижний: Full Table с фильтрами (синхронизированными с графиками)

**Взаимодействие:** Клик по сегменту графика → автоматическое применение фильтра в таблице.

### Prototype 3: Contact Center Focus
**Цель:** Супервизоры и аналитика КЦ.

**Особенности:**
- Фильтры по VDN / Skill / Agent Group
- Метрики SLA (Service Level % — % звонков, отвеченных за X секунд)
- Heatmap по часам × дням недели
- Agent performance table (calls handled, avg handle time, abandon rate)
- Queue/VDN summary cards
- Цветовые пороги (thresholds) для abandoned rate и wait time

### Prototype 4: Modern Cards + Timeline
**Цель:** Современный UX, удобство на планшетах и мобильных.

**Layout:**
- Search-first (большая строка поиска)
- Faceted filters (chips)
- Основной вид: карточки звонков (compact / expanded)
- При клике — боковая панель или modal с Timeline звонка (ring → answer → hold → transfer → end)
- Toggle: Cards / Table
- Полная поддержка dark mode и accessibility (WCAG 2.1 AA)

---

## 6. Архитектура системы

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (SPA)                       │
│  React + TypeScript + Vite + Tailwind + shadcn/ui           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Proto 1  │ │ Proto 2  │ │ Proto 3  │ │ Proto 4  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│         │              shared components & hooks            │
└────────────────────────────┬────────────────────────────────┘
                             │ REST / tRPC
┌────────────────────────────▼────────────────────────────────┐
│                     Backend API                             │
│              FastAPI (Python)  или  NestJS                  │
│  /api/cdr          /api/stats        /api/export            │
│  /api/filters      /api/mock-generate                       │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                     Data Layer                              │
│  PostgreSQL  +  Redis (optional cache)                      │
│  CDR Parser (Avaya formats)  +  Mock Generator              │
└─────────────────────────────────────────────────────────────┘
```

**Рекомендация для агентов:** Начинать с monorepo (Turborepo или просто папки `frontend/` + `backend/`).

---

## 7. Рекомендуемый Tech Stack (строгий)

### Frontend
- **Framework:** React 18/19 + TypeScript 5.x
- **Bundler:** Vite
- **Styling:** Tailwind CSS 3.4+ + shadcn/ui
- **Table:** @tanstack/react-table + @tanstack/react-virtual
- **Charts:** Recharts или Apache ECharts
- **State/Data:** TanStack Query (React Query) + Zustand
- **Forms/Date:** react-hook-form + date-fns + react-day-picker
- **Icons:** lucide-react
- **i18n:** react-i18next
- **Routing:** React Router v6 или TanStack Router

### Backend
- **Основной вариант:** Python 3.12 + FastAPI + SQLAlchemy 2.0 + Pydantic v2 + Alembic
- Альтернатива: NestJS + Prisma / TypeORM
- **DB:** PostgreSQL 16
- **Mock data:** Faker + custom realistic CDR generator

### Tooling
- Docker + Docker Compose
- ESLint + Prettier + Ruff (Python)
- Vitest + Playwright (e2e)
- pnpm или npm workspaces

---

## 8. Структура репозитория (целевая)

```
avaya-cdr-dashboard-prototypes/
├── README.md
├── docs/
│   ├── PROJECT_SPECIFICATION.md          ← этот документ
│   ├── API.md
│   ├── DATA_MODEL.md
│   └── AGENT_GUIDE.md
├── frontend/
│   ├── src/
│   │   ├── prototypes/
│   │   │   ├── classic-table/
│   │   │   ├── analytics/
│   │   │   ├── contact-center/
│   │   │   └── modern-cards/
│   │   ├── components/          # shared
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── types/
│   │   └── mocks/
│   ├── package.json
│   └── ...
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   │   ├── cdr_parser.py
│   │   │   └── mock_generator.py
│   │   └── ...
│   ├── alembic/
│   └── requirements.txt / pyproject.toml
├── docker-compose.yml
└── .github/workflows/ci.yml
```

---

## 9. План реализации для агентов (Phased + INVEST)

### Phase 0: Foundation (1–2 итерации)
- [ ] Инициализация monorepo / frontend + backend
- [ ] Настройка TypeScript, Tailwind, shadcn, ESLint, Prettier
- [ ] Базовый layout + routing между 4 прототипами
- [ ] Mock data generator (минимум 5000–10000 реалистичных записей)
- [ ] SQL-схема + миграции
- [ ] Базовый API: GET /api/cdr (с пагинацией, фильтрами, сортировкой)

**Acceptance Criteria Phase 0:**
- `docker compose up` поднимает frontend + backend + postgres
- Есть страница со списком 4 прототипов
- Mock data генерируется и сохраняется в БД
- API возвращает данные с фильтрами

### Phase 1: Shared Components + Prototype 1 (Classic Table)
- [ ] DateRangePicker, FilterPanel, DataTable, ExportButton, ColumnVisibility
- [ ] Полная реализация Prototype 1
- [ ] Unit + integration tests

**AC:** Все фильтры работают, таблица виртуализирована, экспорт CSV/JSON работает, URL-state синхронизирован.

### Phase 2: Prototype 2 (Analytics)
- [ ] KPI cards
- [ ] 4–5 графиков с drill-down
- [ ] Синхронизация фильтров график ↔ таблица

### Phase 3: Prototype 3 (Contact Center)
- [ ] VDN / Agent metrics
- [ ] Heatmap
- [ ] SLA calculation

### Phase 4: Prototype 4 (Modern Cards)
- [ ] Card view + Timeline
- [ ] Mobile-first polish
- [ ] Accessibility audit

### Phase 5: Polish & Production readiness
- [ ] Dark/Light theme
- [ ] i18n (ru/en)
- [ ] Performance optimization
- [ ] E2E tests (Playwright)
- [ ] Documentation update
- [ ] CI/CD pipeline

---

## 10. Критерии приёмки (Definition of Done) для всего проекта

1. Все 4 прототипа полностью функциональны и переключаемы.
2. Фильтрация + полный табличный просмотр работают во всех прототипах.
3. Mock data ≥ 10 000 записей, реалистичные.
4. Backend API покрывает все необходимые endpoints.
5. Docker Compose работает из коробки.
6. Код проходит lint + typecheck + unit tests.
7. README содержит инструкции по запуску.
8. Нет критических accessibility-ошибок.
9. Документация обновлена.

---

## 11. Инструкции для Agent Club (обязательные правила автономной работы)

1. **Единственный источник истины** — этот документ + файлы в `docs/`.
2. Перед началом любой задачи агент должен:
   - Прочитать соответствующий раздел
   - Создать issue / task в стиле INVEST
   - Указать Acceptance Criteria
3. После каждой фазы — обновить `docs/STATUS.md` и сделать commit с понятным сообщением.
4. Никогда не хардкодить данные — только через mock generator или API.
5. Все UI-компоненты должны быть переиспользуемыми (shared).
6. При сомнениях — выбирать самый простой и надёжный вариант (KISS).
7. После завершения Phase 0–4 создать Pull Request с описанием изменений.
8. Использовать conventional commits.

---

## 12. Примеры mock-данных (фрагмент)

```json
{
  "ucid": "00001001234567890123",
  "start_time": "2026-08-20T14:23:17+02:00",
  "duration_seconds": 187,
  "ring_duration_seconds": 12,
  "calling_number": "79031234567",
  "dialed_number": "84951234567",
  "direction": "inbound",
  "disposition": "answered",
  "vdn": "3001",
  "agent_extension": "1205",
  "account_code": "SALES-42",
  "trunk_in": "T07"
}
```

---

## 13. Дополнительные рекомендации

- Для парсера Avaya CM начинать с Unformatted и Expanded форматов.
- Для IP Office — официальный CSV SMDR.
- Использовать UCID как основной уникальный идентификатор, когда доступен.
- Предусмотреть возможность multi-source (несколько Avaya систем).

---

**Конец спецификации.**

Документ готов к использованию командой агентов.  
Любые отклонения от данного документа должны быть зафиксированы в CHANGELOG и согласованы через issue.

*Создано командой Grok + Harper + Benjamin + Lucas для проекта unhexx/avaya-cdr-dashboard-prototypes.*
