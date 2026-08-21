/**
 * Загрузка страницы CDR и stats; AbortController отменяет устаревшие запросы.
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import type { CdrPage, CdrRecord, CdrStats } from '@/types/cdr'

export type UseCdrOptions = {
  page?: number
  pageSize?: number
  q?: string
  /** Если true — сразу тянем stats с /api/stats */
  withStats?: boolean
}

export function useCdr(options: UseCdrOptions = {}) {
  const page = options.page ?? 1
  const pageSize = options.pageSize ?? 25
  const q = options.q ?? ''
  const withStats = options.withStats ?? false

  const [data, setData] = useState<CdrPage | null>(null)
  const [stats, setStats] = useState<CdrStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [ingesting, setIngesting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const load = useCallback(async () => {
    abortRef.current?.abort()
    const ac = new AbortController()
    abortRef.current = ac

    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
        sort: '-start_time',
      })
      if (q.trim()) params.set('q', q.trim())
      const cdrRes = await fetch(`/api/cdr?${params.toString()}`, {
        signal: ac.signal,
      })
      if (!cdrRes.ok) throw new Error(`cdr ${cdrRes.status}`)
      const cdrJson = (await cdrRes.json()) as CdrPage
      if (ac.signal.aborted) return
      setData(cdrJson)

      if (withStats) {
        const statsRes = await fetch('/api/stats', { signal: ac.signal })
        if (ac.signal.aborted) return
        if (statsRes.ok) {
          setStats((await statsRes.json()) as CdrStats)
        } else {
          setStats({
            total: cdrJson.total,
            talk_seconds: cdrJson.summary?.talk_seconds ?? 0,
          })
        }
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return
      setError('api')
      // Не затираем последний удачный data при сбое — оставляем предыдущую выборку.
    } finally {
      if (!ac.signal.aborted) setLoading(false)
    }
  }, [page, pageSize, q, withStats])

  useEffect(() => {
    void load()
    return () => {
      abortRef.current?.abort()
    }
  }, [load])

  const ingestFixtures = useCallback(async () => {
    setIngesting(true)
    setError(null)
    try {
      const res = await fetch('/api/ingest/fixtures', { method: 'POST' })
      if (!res.ok) throw new Error(String(res.status))
      await load()
    } catch {
      setError('ingest')
    } finally {
      setIngesting(false)
    }
  }, [load])

  return {
    items: (data?.items ?? []) as CdrRecord[],
    page: data?.page ?? page,
    pageSize: data?.page_size ?? pageSize,
    total: data?.total ?? 0,
    summary: data?.summary ?? { count: 0, talk_seconds: 0 },
    stats,
    loading,
    ingesting,
    error,
    reload: load,
    ingestFixtures,
  }
}

/** Форматирование длительности mm:ss. */
export function formatDuration(seconds: number | null | undefined): string {
  const s = Math.max(0, Math.floor(seconds ?? 0))
  const m = Math.floor(s / 60)
  const r = s % 60
  return `${m}:${String(r).padStart(2, '0')}`
}

/** Вариант Badge по disposition. */
export function dispositionVariant(
  d: string | null | undefined,
): 'answered' | 'abandoned' | 'busy' | 'other' {
  if (d === 'answered' || d === 'transferred' || d === 'conferenced') return 'answered'
  if (d === 'abandoned' || d === 'failed') return 'abandoned'
  if (d === 'busy' || d === 'no_answer') return 'busy'
  return 'other'
}

/** Локализованная метка direction/disposition; fallback на сырой ключ. */
export function cdrLabel(
  t: (path: string) => string,
  key: string | null | undefined,
): string {
  const k = key || 'unknown'
  const path = `cdr.${k}`
  const translated = t(path)
  return translated === path ? k : translated
}
