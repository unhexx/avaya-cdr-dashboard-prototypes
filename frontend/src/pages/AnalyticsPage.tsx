/**
 * Аналитика: KPI-карточки + Recharts по выборке CDR.
 */
import { useMemo } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cdrLabel, formatDuration, useCdr } from '@/hooks/useCdr'
import { useI18n } from '@/i18n'

const AQUARIUS = ['#28AFCA', '#A2B7C8', '#24566C', '#5ec8dc', '#7a9aab']
/** Потолок клиентской выборки для KPI/графиков (P6). */
const SAMPLE_CEILING = 500

export function AnalyticsPage() {
  const { t } = useI18n()
  const {
    items,
    total,
    summary,
    stats,
    loading,
    ingesting,
    error,
    reload,
    ingestFixtures,
  } = useCdr({ page: 1, pageSize: SAMPLE_CEILING, withStats: true })

  const kpis = useMemo(() => {
    const answered = items.filter((i) => i.disposition === 'answered').length
    const abandoned = items.filter((i) => i.disposition === 'abandoned').length
    const n = items.length || 1
    const avgDur =
      items.reduce((s, i) => s + (i.duration_seconds || 0), 0) / n
    const avgRing =
      items.reduce((s, i) => s + (i.ring_duration_seconds || 0), 0) / n
    const agents = new Set(
      items.map((i) => i.agent_extension).filter(Boolean),
    ).size
    return {
      answered,
      abandonedPct: Math.round((abandoned / n) * 1000) / 10,
      avgDur,
      avgRing,
      agents,
    }
  }, [items])

  const byHour = useMemo(() => {
    const buckets = Array.from({ length: 24 }, (_, h) => ({
      hour: String(h).padStart(2, '0'),
      count: 0,
    }))
    for (const row of items) {
      if (!row.start_time) continue
      const h = new Date(row.start_time).getHours()
      if (h >= 0 && h < 24) buckets[h].count += 1
    }
    return buckets
  }, [items])

  const byDirection = useMemo(() => {
    const map = new Map<string, number>()
    for (const row of items) {
      const d = String(row.direction || 'unknown')
      map.set(d, (map.get(d) ?? 0) + 1)
    }
    return Array.from(map.entries()).map(([name, value]) => ({
      name: cdrLabel(t, name),
      value,
    }))
  }, [items, t])

  const totalDisplay = stats?.total ?? total
  const talkDisplay = stats?.talk_seconds ?? summary.talk_seconds

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary">{t('analytics.title')}</h1>
          <p className="text-muted-foreground mt-1">{t('analytics.subtitle')}</p>
        </div>
        <Button onClick={() => void ingestFixtures()} disabled={ingesting}>
          {ingesting ? t('common.ingesting') : t('common.ingest')}
        </Button>
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
          <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-8 gap-3">
            <Kpi label={t('common.total')} value={String(totalDisplay)} />
            <Kpi label={t('common.talkSeconds')} value={String(talkDisplay)} />
            <Kpi label={t('analytics.answered')} value={String(kpis.answered)} />
            <Kpi
              label={t('analytics.abandonedPct')}
              value={`${kpis.abandonedPct}%`}
            />
            <Kpi
              label={t('analytics.avgDuration')}
              value={formatDuration(kpis.avgDur)}
            />
            <Kpi
              label={t('analytics.avgRing')}
              value={formatDuration(kpis.avgRing)}
            />
            <Kpi label={t('analytics.uniqueAgents')} value={String(kpis.agents)} />
            <Kpi label={t('analytics.sample')} value={String(items.length)} />
          </div>

          <p className="text-xs text-muted-foreground">
            {t('common.sampleCeiling', { n: SAMPLE_CEILING })}
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{t('analytics.byHour')}</CardTitle>
              </CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={byHour}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#A2B7C8" />
                    <XAxis dataKey="hour" tick={{ fontSize: 11 }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#28AFCA" radius={[2, 2, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{t('analytics.byDirection')}</CardTitle>
              </CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={byDirection}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={90}
                      label
                    >
                      {byDirection.map((_, i) => (
                        <Cell key={i} fill={AQUARIUS[i % AQUARIUS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}

function Kpi({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <CardHeader className="pb-1 pt-3 px-4">
        <CardDescription className="text-xs">{label}</CardDescription>
        <CardTitle className="text-xl text-primary">{value}</CardTitle>
      </CardHeader>
    </Card>
  )
}
