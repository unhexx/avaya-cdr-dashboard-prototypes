import { useCallback, useEffect, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

type NodeStatus = 'ok' | 'degraded' | 'down' | 'unknown' | string

type PbxNode = {
  id: number
  name: string
  kind: string
  host: string | null
  enabled: boolean
  status: NodeStatus | null
  occupancy_pct: number | null
  open_alarms: number
  taken_at: string | null
}

type Alarm = {
  id: number
  pbx_node_id: number | null
  raised_at: string | null
  severity: string
  code: string | null
  resource: string | null
  message: string
}

const KIND_LABEL: Record<string, string> = {
  cm: 'Communication Manager',
  ipo: 'IP Office',
  session_manager: 'Session Manager',
  sbce: 'SBCE',
  other: 'Другое',
}

const STATUS_LABEL: Record<string, string> = {
  ok: 'норма',
  degraded: 'деградация',
  down: 'недоступен',
  unknown: 'нет данных',
}

function statusVariant(status: NodeStatus | null): 'answered' | 'busy' | 'abandoned' | 'other' {
  if (status === 'ok') return 'answered'
  if (status === 'degraded') return 'busy'
  if (status === 'down') return 'abandoned'
  return 'other'
}

function severityVariant(severity: string): 'abandoned' | 'busy' | 'other' | 'default' {
  if (severity === 'critical' || severity === 'major') return 'abandoned'
  if (severity === 'minor') return 'busy'
  return 'other'
}

export function HealthPage() {
  const [nodes, setNodes] = useState<PbxNode[]>([])
  const [alarms, setAlarms] = useState<Alarm[]>([])
  const [loading, setLoading] = useState(true)
  const [ingesting, setIngesting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [pbxRes, alarmRes] = await Promise.all([
        fetch('/api/pbx'),
        fetch('/api/alarms?open=true'),
      ])
      if (!pbxRes.ok) throw new Error(`pbx ${pbxRes.status}`)
      if (!alarmRes.ok) throw new Error(`alarms ${alarmRes.status}`)
      const pbxJson = (await pbxRes.json()) as { items: PbxNode[] }
      const alarmJson = (await alarmRes.json()) as { items: Alarm[] }
      setNodes(pbxJson.items ?? [])
      setAlarms(alarmJson.items ?? [])
    } catch {
      setError('Не удалось загрузить здоровье АТС. Проверьте API.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  async function ingestFixtures() {
    setIngesting(true)
    setError(null)
    try {
      const res = await fetch('/api/ingest/fixtures', { method: 'POST' })
      if (!res.ok) throw new Error(String(res.status))
      await load()
    } catch {
      setError('Не удалось загрузить фикстуры.')
    } finally {
      setIngesting(false)
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary">Здоровье АТС</h1>
          <p className="text-muted-foreground mt-1">
            Снимки SAT/SNMP из фикстур. Живые хосты в этом срезе не опрашиваются.
          </p>
        </div>
        <Button onClick={() => void ingestFixtures()} disabled={ingesting}>
          {ingesting ? 'Загрузка…' : 'Загрузить фикстуры'}
        </Button>
      </div>

      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      {loading ? (
        <p className="text-muted-foreground">Загрузка…</p>
      ) : nodes.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Нет узлов</CardTitle>
            <CardDescription>
              Режим фикстур: нажмите «Загрузить фикстуры», чтобы разобрать SAT
              <span className="font-mono"> status health</span> и mock SNMP.
            </CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {nodes.map((node) => {
            const occ = node.occupancy_pct
            const width = occ == null ? 0 : Math.max(0, Math.min(100, occ))
            return (
              <Card key={node.id}>
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-lg">{node.name}</CardTitle>
                    <Badge variant={statusVariant(node.status)}>
                      {STATUS_LABEL[node.status ?? 'unknown'] ?? node.status}
                    </Badge>
                  </div>
                  <CardDescription>
                    {KIND_LABEL[node.kind] ?? node.kind}
                    {node.host ? ` · ${node.host}` : ''}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <div className="flex justify-between text-xs text-muted-foreground mb-1">
                      <span>Загрузка процессора</span>
                      <span>{occ == null ? '—' : `${occ.toFixed(1)}%`}</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div
                        className={cn(
                          'h-full rounded-full',
                          (occ ?? 0) >= 80 ? 'bg-destructive' : 'bg-primary',
                        )}
                        style={{ width: `${width}%` }}
                      />
                    </div>
                  </div>
                  <p className="text-sm">
                    Открытых аварий:{' '}
                    <span className="font-semibold">{node.open_alarms}</span>
                  </p>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Открытые аварии</CardTitle>
          <CardDescription>Из SAT display alarms и mock-узлов</CardDescription>
        </CardHeader>
        <CardContent>
          {alarms.length === 0 ? (
            <p className="text-sm text-muted-foreground">Открытых аварий нет.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b">
                    <th className="py-2 pr-3 font-medium">Серьёзность</th>
                    <th className="py-2 pr-3 font-medium">Код</th>
                    <th className="py-2 pr-3 font-medium">Ресурс</th>
                    <th className="py-2 pr-3 font-medium">Сообщение</th>
                    <th className="py-2 font-medium">Время</th>
                  </tr>
                </thead>
                <tbody>
                  {alarms.map((alarm) => (
                    <tr key={alarm.id} className="border-b last:border-0">
                      <td className="py-2 pr-3">
                        <Badge variant={severityVariant(alarm.severity)}>{alarm.severity}</Badge>
                      </td>
                      <td className="py-2 pr-3 font-mono text-xs">{alarm.code ?? '—'}</td>
                      <td className="py-2 pr-3 font-mono text-xs">{alarm.resource ?? '—'}</td>
                      <td className="py-2 pr-3">{alarm.message}</td>
                      <td className="py-2 text-muted-foreground whitespace-nowrap">
                        {alarm.raised_at ? alarm.raised_at.replace('T', ' ').replace('+00:00', ' UTC') : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
