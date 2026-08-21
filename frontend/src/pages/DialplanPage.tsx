import { useCallback, useEffect, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

type DialplanEntry = {
  id: number
  source: string
  match_prefix: string
  min_digits: number | null
  max_digits: number | null
  route: string | null
  call_type: string | null
  node_number: string | null
  location: string | null
  raw: string | null
  synced_at: string | null
}

const SOURCE_LABEL: Record<string, string> = {
  ars: 'ARS (CM)',
  dialplan: 'Dialplan analysis',
  ipo_shortcode: 'IPO short code',
  ipo_ars: 'IPO ARS',
}

export function DialplanPage() {
  const [items, setItems] = useState<DialplanEntry[]>([])
  const [q, setQ] = useState('')
  const [source, setSource] = useState('')
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async (query: string, src: string) => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (query.trim()) params.set('q', query.trim())
      if (src) params.set('source', src)
      const res = await fetch(`/api/dialplan?${params.toString()}`)
      if (!res.ok) throw new Error(`dialplan ${res.status}`)
      const json = (await res.json()) as { items: DialplanEntry[]; total: number }
      setItems(json.items ?? [])
    } catch {
      setError('Не удалось загрузить план нумерации. Сначала выполните синхронизацию.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load(q, source)
  }, [load, q, source])

  async function syncFixtures() {
    setSyncing(true)
    setError(null)
    try {
      const res = await fetch('/api/dialplan/sync', { method: 'POST' })
      if (!res.ok) throw new Error(String(res.status))
      await load(q, source)
    } catch {
      setError('Не удалось синхронизировать фикстуры ARS/IPO.')
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary">План нумерации</h1>
          <p className="text-muted-foreground mt-1">
            Поиск longest-prefix по ARS Analysis и IPO short codes из фикстур.
          </p>
        </div>
        <Button onClick={() => void syncFixtures()} disabled={syncing}>
          {syncing ? 'Синхронизация…' : 'Синхронизировать фикстуры'}
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Поиск</CardTitle>
          <CardDescription>
            Введите набранный номер — сверху окажутся самые длинные совпадающие префиксы.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <input
            type="search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Например 81012345678"
            className="flex h-10 w-full max-w-md rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            aria-label="Номер для поиска"
          />
          <select
            value={source}
            onChange={(e) => setSource(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
            aria-label="Источник"
          >
            <option value="">Все источники</option>
            <option value="ars">ARS (CM)</option>
            <option value="ipo_shortcode">IPO short code</option>
          </select>
        </CardContent>
      </Card>

      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Совпадения</CardTitle>
          <CardDescription>
            {loading ? 'Загрузка…' : `Найдено: ${items.length}`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!loading && items.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Пусто. Нажмите «Синхронизировать фикстуры», затем введите номер (например{' '}
              <span className="font-mono">810</span>).
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b">
                    <th className="py-2 pr-3 font-medium">Префикс</th>
                    <th className="py-2 pr-3 font-medium">Источник</th>
                    <th className="py-2 pr-3 font-medium">Min/Max</th>
                    <th className="py-2 pr-3 font-medium">Маршрут</th>
                    <th className="py-2 pr-3 font-medium">Тип</th>
                    <th className="py-2 pr-3 font-medium">Узел / номер</th>
                    <th className="py-2 font-medium">Локация</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((row) => (
                    <tr key={row.id} className="border-b last:border-0">
                      <td className="py-2 pr-3 font-mono font-semibold">{row.match_prefix}</td>
                      <td className="py-2 pr-3">
                        <Badge variant="secondary">
                          {SOURCE_LABEL[row.source] ?? row.source}
                        </Badge>
                      </td>
                      <td className="py-2 pr-3 font-mono text-xs">
                        {row.min_digits == null && row.max_digits == null
                          ? '—'
                          : `${row.min_digits ?? '—'} / ${row.max_digits ?? '—'}`}
                      </td>
                      <td className="py-2 pr-3 font-mono text-xs">{row.route ?? '—'}</td>
                      <td className="py-2 pr-3">{row.call_type ?? '—'}</td>
                      <td className="py-2 pr-3 font-mono text-xs">{row.node_number ?? '—'}</td>
                      <td className="py-2 text-muted-foreground">{row.location ?? '—'}</td>
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
