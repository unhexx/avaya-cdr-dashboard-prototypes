/**
 * Простой i18n: ru по умолчанию (ADR 0011), переключатель в Header.
 */
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import en from './en.json'
import ru from './ru.json'

export type Lang = 'ru' | 'en'

type Dict = typeof ru

const catalogs: Record<Lang, Dict> = { ru, en }

type I18nContextValue = {
  lang: Lang
  setLang: (lang: Lang) => void
  t: (path: string, vars?: Record<string, string | number>) => string
}

const I18nContext = createContext<I18nContextValue | null>(null)

const STORAGE_KEY = 'aquarius-lang'

function readInitialLang(): Lang {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'en' || stored === 'ru') return stored
  } catch {
    /* ignore */
  }
  return 'ru'
}

function lookup(dict: Dict, path: string): string | undefined {
  const parts = path.split('.')
  let cur: unknown = dict
  for (const p of parts) {
    if (cur == null || typeof cur !== 'object') return undefined
    cur = (cur as Record<string, unknown>)[p]
  }
  return typeof cur === 'string' ? cur : undefined
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(readInitialLang)

  const setLang = useCallback((next: Lang) => {
    setLangState(next)
    try {
      localStorage.setItem(STORAGE_KEY, next)
    } catch {
      /* ignore */
    }
  }, [])

  const t = useCallback(
    (path: string, vars?: Record<string, string | number>) => {
      let text = lookup(catalogs[lang], path) ?? lookup(catalogs.ru, path) ?? path
      if (vars) {
        for (const [k, v] of Object.entries(vars)) {
          text = text.replace(`{${k}}`, String(v))
        }
      }
      return text
    },
    [lang],
  )

  const value = useMemo(() => ({ lang, setLang, t }), [lang, setLang, t])

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useI18n вне I18nProvider')
  return ctx
}
