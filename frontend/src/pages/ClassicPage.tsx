/**
 * Классическая таблица CDR — TanStack Table + пагинация GET /api/cdr.
 */
import { useMemo, useState } from 'react'
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
} from '@tanstack/react-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cdrLabel, dispositionVariant, formatDuration, useCdr } from '@/hooks/useCdr'
import { useI18n } from '@/i18n'
import type { CdrRecord } from '@/types/cdr'

export function ClassicPage() {
  const { t } = useI18n()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)
  const [q, setQ] = useState('')
  const [qApplied, setQApplied] = useState('')

  const {
    items,
    total,
    summary,
    loading,
    ingesting,
    error,
    reload,
    ingestFixtures,
  } = useCdr({ page, pageSize, q: qApplied })

  const columns = useMemo<ColumnDef<CdrRecord>[]>(
    () => [
      {
        accessorKey: 'start_time',
        header: t('cdr.startTime'),
        cell: ({ getValue }) => {
          const v = getValue<string | null>()
          if (!v) return '—'
          try {
            return new Date(v).toLocaleString()
          } catch {
            return v
          }
        },
      },
      {
        accessorKey: 'calling_number',
        header: t('cdr.calling'),
        cell: ({ getValue }) => getValue<string | null>() ?? '—',
      },
      {
        accessorKey: 'dialed_number',
        header: t('cdr.dialed'),
        cell: ({ getValue }) => getValue<string | null>() ?? '—',
      },
      {
        accessorKey: 'direction',
        header: t('cdr.direction'),
        cell: ({ getValue }) => cdrLabel(t, String(getValue() ?? 'unknown')),
      },
      {
        accessorKey: 'disposition',
        header: t('cdr.disposition'),
        cell: ({ getValue }) => {
          const d = String(getValue() ?? 'other')
          return <Badge variant={dispositionVariant(d)}>{cdrLabel(t, d)}</Badge>
        },
      },
      {
        accessorKey: 'duration_seconds',
        header: t('cdr.duration'),
        cell: ({ getValue }) => formatDuration(getValue<number>()),
      },
      {
        accessorKey: 'ring_duration_seconds',
        header: t('cdr.ring'),
        cell: ({ getValue }) => formatDuration(getValue<number>()),
      },
      {
        accessorKey: 'vdn',
        header: t('cdr.vdn'),
        cell: ({ getValue }) => getValue<string | null>() ?? '—',
      },
      {
        accessorKey: 'agent_extension',
        header: t('cdr.agent'),
        cell: ({ getValue }) => getValue<string | null>() ?? '—',
      },
    ],
    [t],
  )

  const table = useReactTable({
    data: items,
    columns,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
    pageCount: Math.max(1, Math.ceil(total / pageSize)),
  })

  const pageCount = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary">{t('classic.title')}</h1>
          <p className="text-muted-foreground mt-1">{t('classic.subtitle')}</p>
        </div>
        <Button onClick={() => void ingestFixtures()} disabled={ingesting}>
          {ingesting ? t('common.ingesting') : t('common.ingest')}
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <input
          className="border border-input rounded-md px-3 py-2 text-sm bg-background min-w-[200px]"
          placeholder={t('common.search')}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              setPage(1)
              setQApplied(q)
            }
          }}
          aria-label={t('common.search')}
        />
        <Button
          variant="secondary"
          onClick={() => {
            setPage(1)
            setQApplied(q)
          }}
        >
          {t('common.search')}
        </Button>
        <span className="text-sm text-muted-foreground">
          {t('common.total')}: {total} · {t('common.talkSeconds')}:{' '}
          {summary.talk_seconds}
        </span>
      </div>

      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {t('common.error')}{' '}
          <button type="button" className="underline" onClick={() => void reload()}>
            {t('common.retry')}
          </button>
        </p>
      ) : null}

      {loading ? (
        <p className="text-muted-foreground">{t('common.loading')}</p>
      ) : items.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>{t('common.empty')}</CardTitle>
            <CardDescription>{t('common.emptyHint')}</CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <>
          <div className="rounded-md border border-border overflow-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted sticky top-0 z-10">
                {table.getHeaderGroups().map((hg) => (
                  <tr key={hg.id}>
                    {hg.headers.map((h) => (
                      <th
                        key={h.id}
                        className="text-left font-medium px-3 py-2 whitespace-nowrap"
                        scope="col"
                      >
                        {flexRender(h.column.columnDef.header, h.getContext())}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    className="border-t border-border hover:bg-muted/40"
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-3 py-2 whitespace-nowrap">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex flex-wrap items-center gap-3 justify-between">
            <div className="flex items-center gap-2 text-sm">
              <Button
                variant="secondary"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                {t('common.prev')}
              </Button>
              <span>
                {t('common.page')} {page} {t('common.of')} {pageCount}
              </span>
              <Button
                variant="secondary"
                disabled={page >= pageCount}
                onClick={() => setPage((p) => p + 1)}
              >
                {t('common.next')}
              </Button>
            </div>
            <select
              className="border border-input rounded-md px-2 py-1 text-sm bg-background"
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value))
                setPage(1)
              }}
              aria-label={t('common.pageSize')}
            >
              {[10, 25, 50, 100, 500].map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </div>
        </>
      )}
    </div>
  )
}
