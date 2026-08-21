import { useCallback, useEffect, useRef, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

type Recording = {
  id: number
  ucid: string | null
  start_time: string | null
  duration_seconds: number | null
  calling_number: string | null
  dialed_number: string | null
  filename: string | null
  mime_type: string | null
  encrypted: boolean
  encryption_hint: string | null
  sql_source_id: string | null
}

const ENCRYPTED_MSG =
  'Запись зашифрована IP Office (R11.1+). Расшифровка недоступна — только метаданные.'

export function RecordingsPage() {
  const [items, setItems] = useState<Recording[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [playError, setPlayError] = useState<string | null>(null)
  const [playingId, setPlayingId] = useState<number | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const blobUrlRef = useRef<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/recordings?page_size=50')
      if (!res.ok) throw new Error(`recordings ${res.status}`)
      const json = (await res.json()) as { items: Recording[]; total: number }
      setItems(json.items ?? [])
      setTotal(json.total ?? 0)
    } catch {
      setError('Не удалось загрузить список записей')
      setItems([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
    return () => {
      if (blobUrlRef.current) URL.revokeObjectURL(blobUrlRef.current)
      audioRef.current?.pause()
    }
  }, [load])

  const stopAudio = () => {
    audioRef.current?.pause()
    if (blobUrlRef.current) {
      URL.revokeObjectURL(blobUrlRef.current)
      blobUrlRef.current = null
    }
    setPlayingId(null)
  }

  const play = async (rec: Recording) => {
    setPlayError(null)
    stopAudio()
    try {
      const res = await fetch(`/api/recordings/${rec.id}/audio`)
      if (res.status === 409) {
        const body = (await res.json()) as { error?: { reason?: string } }
        if (body.error?.reason === 'ipo_encrypted_r11') {
          setPlayError(ENCRYPTED_MSG)
        } else {
          setPlayError(ENCRYPTED_MSG)
        }
        return
      }
      if (!res.ok) {
        setPlayError(`Аудио недоступно (${res.status})`)
        return
      }
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      blobUrlRef.current = url
      const audio = new Audio(url)
      audioRef.current = audio
      setPlayingId(rec.id)
      audio.onended = () => setPlayingId(null)
      await audio.play()
    } catch {
      setPlayError('Ошибка воспроизведения')
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-primary">Записи</h1>
          <p className="text-sm text-muted-foreground">
            Метаданные из sql-source; аудио по запросу (200 WAV / 409 encrypted)
          </p>
        </div>
        <Button variant="outline" onClick={() => void load()} disabled={loading}>
          Обновить
        </Button>
      </div>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6 text-destructive">{error}</CardContent>
        </Card>
      )}

      {playError && (
        <Card className="border-amber-500/50 bg-amber-500/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Зашифрованная запись</CardTitle>
            <CardDescription>{playError}</CardDescription>
          </CardHeader>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Каталог</CardTitle>
          <CardDescription>
            {loading ? 'Загрузка…' : `Всего: ${total}`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {items.length === 0 && !loading ? (
            <p className="text-muted-foreground text-sm">Нет записей. Проверьте фикстуры sql/recordings.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-3">ID</th>
                    <th className="py-2 pr-3">Время</th>
                    <th className="py-2 pr-3">От</th>
                    <th className="py-2 pr-3">Кому</th>
                    <th className="py-2 pr-3">Длит.</th>
                    <th className="py-2 pr-3">UCID</th>
                    <th className="py-2 pr-3">Статус</th>
                    <th className="py-2">Действие</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((rec) => (
                    <tr key={rec.id} className="border-b border-border/60">
                      <td className="py-2 pr-3 font-mono">{rec.id}</td>
                      <td className="py-2 pr-3 whitespace-nowrap">
                        {rec.start_time?.replace('T', ' ').replace('Z', '') ?? '—'}
                      </td>
                      <td className="py-2 pr-3 font-mono">{rec.calling_number ?? '—'}</td>
                      <td className="py-2 pr-3 font-mono">{rec.dialed_number ?? '—'}</td>
                      <td className="py-2 pr-3">{rec.duration_seconds ?? '—'} с</td>
                      <td className="py-2 pr-3 font-mono text-xs">{rec.ucid ?? '—'}</td>
                      <td className="py-2 pr-3">
                        {rec.encrypted ? (
                          <Badge variant="busy">encrypted</Badge>
                        ) : (
                          <Badge variant="answered">ok</Badge>
                        )}
                      </td>
                      <td className="py-2">
                        <Button
                          size="sm"
                          variant={playingId === rec.id ? 'default' : 'outline'}
                          onClick={() => void play(rec)}
                        >
                          {rec.encrypted ? 'Метаданные' : playingId === rec.id ? 'Играет…' : 'Слушать'}
                        </Button>
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
