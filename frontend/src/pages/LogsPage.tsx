import { useCallback, useEffect, useRef, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

type LogKind = 'sip' | 'e1' | 'alarm'

type LogEvent = {
  id: number
  kind: string
  event_time: string | null
  host: string | null
  severity: string | null
  call_id: string | null
  sip_method: string | null
  sip_response: number | null
  ds1_board: string | null
  alarm_type: string | null
  message: string
  raw: string | null
}

const KIND_TABS: { id: LogKind; label: string }[] = [
  { id: 'sip', label: 'SIP' },
  { id: 'e1', label: 'E1 / DS1' },
  { id: 'alarm', label: 'Аварии' },
]

const DEBOUNCE_MS = 300

function severityVariant(severity: string | null): 'abandoned' | 'busy' | 'other' | 'default' {
  if (!severity) return 'default'
  if (severity === 'emerg' || severity === 'alert' || severity === 'crit' || severity === 'err') {
    return 'abandoned'
  }
  if (severity === 'warning') return 'busy'
  return 'other'
}

export function LogsPage() {
  const [kind, setKind] = useState<LogKind>('sip')
  const [items, setItems] = useState<LogEvent[]>([])
  const [total, setTotal] = useState(0)
  const [q, setQ] = useState('')
  const [callId, setCallId] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const kindRef = useRef(kind)
  const skipFilterDebounce = useRef(true)
  kindRef.current = kind

  const fetchLogs = useCallback(async (nextKind: LogKind, nextQ: string, nextCallId: string) => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ kind: nextKind })
      if (nextQ.trim()) params.set('q', nextQ.trim())
      if (nextCallId.trim()) params.set('call_id', nextCallId.trim())
      const res = await fetch(`/api/logs?${params}`)
      if (!res.ok) throw new Error(String(res.status))
      const json = (await res.json()) as { items: LogEvent[]; total: number }
      setItems(json.items ?? [])
      setTotal(json.total ?? 0)
    } catch {
      setError('Не удалось загрузить журнал. Проверьте API.')
    } finally {
      setLoading(false)
    }
  }, [])

  // Вкладка kind — сразу (с текущими q/callId)
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
      debounceRef.current = null
    }
    void fetchLogs(kind, q, callId)
    // eslint-disable-next-line react-hooks/exhaustive-deps -- q/callId через debounce
  }, [kind, fetchLogs])

  // q / callId — debounce 300 мс (пропуск первого mount)
  useEffect(() => {
    if (skipFilterDebounce.current) {
      skipFilterDebounce.current = false
      return
    }
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      void fetchLogs(kindRef.current, q, callId)
    }, DEBOUNCE_MS)
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [q, callId, fetchLogs])

  function applyFilters() {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
      debounceRef.current = null
    }
    void fetchLogs(kind, q, callId)
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-primary">Журналы SIP / E1</h1>
        <p className="text-muted-foreground mt-1">
          Syslog Session Manager, SBCE и MEDPRO из фикстур (без pcap).
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {KIND_TABS.map((tab) => (
          <Button
            key={tab.id}
            variant={kind === tab.id ? 'default' : 'outline'}
            size="sm"
            onClick={() => setKind(tab.id)}
          >
            {tab.label}
          </Button>
        ))}
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Фильтры</CardTitle>
          <CardDescription>Поиск по сообщению и Call-ID (debounce 300 мс)</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3 items-end">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-muted-foreground">Сообщение (q)</span>
            <input
              className="border rounded-md px-3 py-2 bg-background min-w-[12rem]"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') applyFilters()
              }}
              placeholder="INVITE, LOS…"
            />
          </label>
          {kind === 'sip' ? (
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-muted-foreground">Call-ID</span>
              <input
                className="border rounded-md px-3 py-2 bg-background min-w-[12rem] font-mono text-xs"
                value={callId}
                onChange={(e) => setCallId(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') applyFilters()
                }}
                placeholder="c7f1abcd@sm.local"
              />
            </label>
          ) : null}
          <Button onClick={applyFilters} disabled={loading}>
            {loading ? 'Загрузка…' : 'Обновить'}
          </Button>
        </CardContent>
      </Card>

      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>
            События{' '}
            <span className="text-muted-foreground font-normal text-base">({total})</span>
          </CardTitle>
          <CardDescription>
            {kind === 'sip' && 'INVITE / ответы / BYE из session-manager и SBCE'}
            {kind === 'e1' && 'LOS / RAI / AIS / SLIP с плат DS1 MEDPRO'}
            {kind === 'alarm' && 'Строки ALARM (в фикстурах может быть пусто)'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-muted-foreground">Загрузка…</p>
          ) : items.length === 0 ? (
            <p className="text-sm text-muted-foreground">Нет событий для выбранного вида.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b">
                    <th className="py-2 pr-3 font-medium">Время</th>
                    <th className="py-2 pr-3 font-medium">Хост</th>
                    <th className="py-2 pr-3 font-medium">Уровень</th>
                    {kind === 'sip' ? (
                      <>
                        <th className="py-2 pr-3 font-medium">Метод</th>
                        <th className="py-2 pr-3 font-medium">Ответ</th>
                        <th className="py-2 pr-3 font-medium">Call-ID</th>
                      </>
                    ) : null}
                    {kind === 'e1' ? (
                      <>
                        <th className="py-2 pr-3 font-medium">Плата</th>
                        <th className="py-2 pr-3 font-medium">Тип</th>
                      </>
                    ) : null}
                    <th className="py-2 font-medium">Сообщение</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((ev) => (
                    <tr key={ev.id} className="border-b last:border-0 align-top">
                      <td className="py-2 pr-3 text-muted-foreground whitespace-nowrap">
                        {ev.event_time
                          ? ev.event_time
                              .replace('T', ' ')
                              .replace('+00:00', ' UTC')
                              .replace('Z', ' UTC')
                          : '—'}
                      </td>
                      <td className="py-2 pr-3 font-mono text-xs">{ev.host ?? '—'}</td>
                      <td className="py-2 pr-3">
                        {ev.severity ? (
                          <Badge variant={severityVariant(ev.severity)}>{ev.severity}</Badge>
                        ) : (
                          '—'
                        )}
                      </td>
                      {kind === 'sip' ? (
                        <>
                          <td className="py-2 pr-3 font-mono text-xs">{ev.sip_method ?? '—'}</td>
                          <td className="py-2 pr-3 font-mono text-xs">
                            {ev.sip_response != null ? (
                              <span
                                className={cn(
                                  ev.sip_response >= 500
                                    ? 'text-destructive'
                                    : ev.sip_response >= 400
                                      ? 'text-amber-600'
                                      : '',
                                )}
                              >
                                {ev.sip_response}
                              </span>
                            ) : (
                              '—'
                            )}
                          </td>
                          <td className="py-2 pr-3 font-mono text-xs break-all">
                            {ev.call_id ?? '—'}
                          </td>
                        </>
                      ) : null}
                      {kind === 'e1' ? (
                        <>
                          <td className="py-2 pr-3 font-mono text-xs">{ev.ds1_board ?? '—'}</td>
                          <td className="py-2 pr-3 font-mono text-xs">{ev.alarm_type ?? '—'}</td>
                        </>
                      ) : null}
                      <td className="py-2 max-w-xl break-words">{ev.message}</td>
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
