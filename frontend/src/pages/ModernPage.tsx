/**
 * Современные карточки + простой таймлайн (ring → answer → hold → end).
 */
import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cdrLabel, dispositionVariant, formatDuration, useCdr } from '@/hooks/useCdr'
import { useI18n } from '@/i18n'
import type { CdrRecord } from '@/types/cdr'
import { cn } from '@/lib/utils'

export function ModernPage() {
  const { t } = useI18n()
  const [q, setQ] = useState('')
  const [selected, setSelected] = useState<CdrRecord | null>(null)
  const {
    items,
    loading,
    ingesting,
    error,
    reload,
    ingestFixtures,
  } = useCdr({ page: 1, pageSize: 100 })

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase()
    if (!needle) return items
    return items.filter((r) => {
      const hay = [
        r.calling_number,
        r.dialed_number,
        r.vdn,
        r.agent_extension,
        r.ucid,
        r.disposition,
        r.direction,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      return hay.includes(needle)
    })
  }, [items, q])

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary">{t('modern.title')}</h1>
          <p className="text-muted-foreground mt-1">{t('modern.subtitle')}</p>
        </div>
        <Button onClick={() => void ingestFixtures()} disabled={ingesting}>
          {ingesting ? t('common.ingesting') : t('common.ingest')}
        </Button>
      </div>

      <input
        className="border border-input rounded-md px-3 py-2 text-sm bg-background w-full max-w-md"
        placeholder={t('common.search')}
        value={q}
        onChange={(e) => setQ(e.target.value)}
        aria-label={t('common.search')}
      />

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
      ) : filtered.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>{t('common.empty')}</CardTitle>
            <CardDescription>{t('common.emptyHint')}</CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
            {filtered.map((row) => {
              const disp = String(row.disposition ?? 'other')
              const active = selected?.id === row.id
              return (
                <button
                  key={row.id}
                  type="button"
                  onClick={() => setSelected(row)}
                  className={cn(
                    'text-left rounded-lg border border-border bg-card p-4 transition-shadow hover:shadow-md focus:outline-none focus:ring-2 focus:ring-ring',
                    active && 'ring-2 ring-primary border-primary',
                  )}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <span className="font-mono text-sm">
                      {row.calling_number ?? '—'} → {row.dialed_number ?? '—'}
                    </span>
                    <Badge variant={dispositionVariant(disp)}>{cdrLabel(t, disp)}</Badge>
                  </div>
                  <div className="text-xs text-muted-foreground space-y-1">
                    <div>
                      {row.start_time
                        ? new Date(row.start_time).toLocaleString()
                        : '—'}
                    </div>
                    <div>
                      {t('cdr.duration')}: {formatDuration(row.duration_seconds)} ·{' '}
                      {t('cdr.vdn')}: {row.vdn ?? '—'} · {t('cdr.agent')}:{' '}
                      {row.agent_extension ?? t('modern.noAgent')}
                    </div>
                  </div>
                </button>
              )
            })}
          </div>

          <aside className="lg:sticky lg:top-20 h-fit">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">{t('modern.timeline')}</CardTitle>
                <CardDescription>
                  {selected
                    ? selected.ucid ?? `#${selected.id}`
                    : '—'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {selected ? (
                  <Timeline record={selected} />
                ) : (
                  <p className="text-sm text-muted-foreground">—</p>
                )}
              </CardContent>
            </Card>
          </aside>
        </div>
      )}
    </div>
  )
}

function Timeline({ record }: { record: CdrRecord }) {
  const { t } = useI18n()
  const ring = record.ring_duration_seconds ?? 0
  const talk = record.duration_seconds ?? 0
  const hold = record.hold_duration_seconds ?? 0
  const answered = record.disposition === 'answered' || talk > 0

  const steps = [
    {
      key: 'ring',
      label: t('modern.ringPhase'),
      detail: formatDuration(ring),
      done: true,
      color: '#A2B7C8',
    },
    {
      key: 'answer',
      label: t('modern.answerPhase'),
      detail: answered ? formatDuration(talk) : '—',
      done: answered,
      color: '#28AFCA',
    },
    {
      key: 'hold',
      label: t('modern.holdPhase'),
      detail: hold > 0 ? formatDuration(hold) : '—',
      done: hold > 0,
      color: '#24566C',
    },
    {
      key: 'end',
      label: t('modern.endPhase'),
      detail: String(record.disposition ?? '—'),
      done: true,
      color: '#24566C',
    },
  ]

  return (
    <ol className="space-y-4">
      {steps.map((s, idx) => (
        <li key={s.key} className="flex gap-3">
          <div className="flex flex-col items-center">
            <span
              className="w-3 h-3 rounded-full shrink-0"
              style={{
                backgroundColor: s.done ? s.color : '#e5e7eb',
              }}
            />
            {idx < steps.length - 1 ? (
              <span className="w-px flex-1 bg-border my-1 min-h-[20px]" />
            ) : null}
          </div>
          <div className="pb-2">
            <div className="text-sm font-medium">{s.label}</div>
            <div className="text-xs text-muted-foreground">{s.detail}</div>
          </div>
        </li>
      ))}
    </ol>
  )
}
