/**
 * Контакт-центр: SLA, таблица агентов, карточки VDN.
 */
import { useMemo } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatDuration, useCdr } from '@/hooks/useCdr'
import { useI18n } from '@/i18n'
import { SLA_THRESHOLD_SECONDS } from '@/types/cdr'

/** Потолок клиентской выборки для SLA/агентов/VDN (P6). */
const SAMPLE_CEILING = 500

type AgentRow = {
  agent: string
  handled: number
  avgHandle: number
  abandonRate: number
}

type VdnRow = {
  vdn: string
  total: number
  answered: number
  abandoned: number
  abandonPct: number
  slaPct: number
}

export function ContactCenterPage() {
  const { t } = useI18n()
  const {
    items,
    loading,
    ingesting,
    error,
    reload,
    ingestFixtures,
  } = useCdr({ page: 1, pageSize: SAMPLE_CEILING })

  const slaPct = useMemo(() => {
    const inboundish = items.filter(
      (i) =>
        i.disposition === 'answered' ||
        i.disposition === 'abandoned' ||
        i.disposition === 'no_answer',
    )
    if (inboundish.length === 0) return 0
    const ok = inboundish.filter(
      (i) =>
        i.disposition === 'answered' &&
        (i.ring_duration_seconds ?? 99) <= SLA_THRESHOLD_SECONDS,
    ).length
    return Math.round((ok / inboundish.length) * 1000) / 10
  }, [items])

  const agents = useMemo(() => {
    const map = new Map<
      string,
      { handled: number; talk: number; abandoned: number }
    >()
    for (const row of items) {
      const a = row.agent_extension
      if (!a) continue
      const cur = map.get(a) ?? { handled: 0, talk: 0, abandoned: 0 }
      cur.handled += 1
      cur.talk += row.duration_seconds || 0
      if (row.disposition === 'abandoned') cur.abandoned += 1
      map.set(a, cur)
    }
    const rows: AgentRow[] = Array.from(map.entries()).map(([agent, v]) => ({
      agent,
      handled: v.handled,
      avgHandle: v.handled ? v.talk / v.handled : 0,
      abandonRate: v.handled ? Math.round((v.abandoned / v.handled) * 1000) / 10 : 0,
    }))
    rows.sort((a, b) => b.handled - a.handled)
    return rows
  }, [items])

  const vdns = useMemo(() => {
    // slaOffered = inboundish (answered|abandoned|no_answer) — как у карточки SLA сверху
    const map = new Map<
      string,
      {
        total: number
        answered: number
        abandoned: number
        slaOk: number
        slaOffered: number
      }
    >()
    for (const row of items) {
      const v = row.vdn
      if (!v) continue
      const cur = map.get(v) ?? {
        total: 0,
        answered: 0,
        abandoned: 0,
        slaOk: 0,
        slaOffered: 0,
      }
      cur.total += 1
      const d = row.disposition
      const inboundish =
        d === 'answered' || d === 'abandoned' || d === 'no_answer'
      if (inboundish) cur.slaOffered += 1
      if (d === 'answered') {
        cur.answered += 1
        if ((row.ring_duration_seconds ?? 99) <= SLA_THRESHOLD_SECONDS) cur.slaOk += 1
      }
      if (d === 'abandoned') cur.abandoned += 1
      map.set(v, cur)
    }
    const rows: VdnRow[] = Array.from(map.entries()).map(([vdn, v]) => ({
      vdn,
      total: v.total,
      answered: v.answered,
      abandoned: v.abandoned,
      abandonPct: v.total ? Math.round((v.abandoned / v.total) * 1000) / 10 : 0,
      slaPct: v.slaOffered
        ? Math.round((v.slaOk / v.slaOffered) * 1000) / 10
        : 0,
    }))
    rows.sort((a, b) => b.total - a.total)
    return rows
  }, [items])

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary">{t('cc.title')}</h1>
          <p className="text-muted-foreground mt-1">{t('cc.subtitle')}</p>
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
          <p className="text-xs text-muted-foreground">
            {t('common.sampleCeiling', { n: SAMPLE_CEILING })}
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>
                  {t('cc.sla', { n: SLA_THRESHOLD_SECONDS })}
                </CardDescription>
                <CardTitle className="text-3xl text-primary">{slaPct}%</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>{t('cc.agents')}</CardDescription>
                <CardTitle className="text-3xl text-primary">{agents.length}</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>{t('cc.vdnSummary')}</CardDescription>
                <CardTitle className="text-3xl text-primary">{vdns.length}</CardTitle>
              </CardHeader>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">{t('cc.agents')}</CardTitle>
            </CardHeader>
            <CardContent className="overflow-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    <th className="text-left px-3 py-2">{t('cdr.agent')}</th>
                    <th className="text-left px-3 py-2">{t('cc.handled')}</th>
                    <th className="text-left px-3 py-2">{t('cc.avgHandle')}</th>
                    <th className="text-left px-3 py-2">{t('cc.abandonRate')}</th>
                  </tr>
                </thead>
                <tbody>
                  {agents.map((a) => (
                    <tr key={a.agent} className="border-t border-border">
                      <td className="px-3 py-2 font-mono">{a.agent}</td>
                      <td className="px-3 py-2">{a.handled}</td>
                      <td className="px-3 py-2">{formatDuration(a.avgHandle)}</td>
                      <td className="px-3 py-2">
                        <Badge variant={a.abandonRate > 8 ? 'abandoned' : 'answered'}>
                          {a.abandonRate}%
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>

          <div>
            <h2 className="text-lg font-semibold mb-3">{t('cc.vdnSummary')}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
              {vdns.map((v) => (
                <Card key={v.vdn}>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base font-mono">VDN {v.vdn}</CardTitle>
                      <Badge
                        variant={
                          v.abandonPct > 8
                            ? 'abandoned'
                            : v.slaPct < 80
                              ? 'busy'
                              : 'answered'
                        }
                      >
                        SLA {v.slaPct}%
                      </Badge>
                    </div>
                    <CardDescription>
                      {v.total} · {t('analytics.answered')} {v.answered} ·{' '}
                      {t('analytics.abandonedPct')} {v.abandonPct}%
                    </CardDescription>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
