import { Link, useLocation } from 'react-router-dom'
import { useI18n, type Lang } from '@/i18n'
import { cn } from '@/lib/utils'

export function Header() {
  const { t, lang, setLang } = useI18n()
  const { pathname } = useLocation()

  const links: { to: string; label: string; match?: string[] }[] = [
    { to: '/classic', label: t('nav.classic'), match: ['/', '/classic'] },
    { to: '/analytics', label: t('nav.analytics') },
    {
      to: '/contact-center',
      label: t('nav.contactCenter'),
      match: ['/contact-center', '/cc'],
    },
    { to: '/modern', label: t('nav.modern'), match: ['/modern', '/cards'] },
    { to: '/health', label: t('nav.health') },
    { to: '/dialplan', label: t('nav.dialplan') },
    { to: '/logs', label: t('nav.logs') },
    { to: '/recordings', label: t('nav.recordings') },
  ]

  function isActive(to: string, match?: string[]) {
    const paths = match ?? [to]
    return paths.some((p) => pathname === p)
  }

  return (
    <header className="border-b border-border bg-card sticky top-0 z-50">
      <div className="container mx-auto flex items-center justify-between h-14 px-4 gap-4">
        <Link to="/" className="flex items-center gap-3 shrink-0">
          <svg
            width="32"
            height="32"
            viewBox="0 0 32 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-label="Aquarius pixel logo"
          >
            <rect x="4" y="4" width="10" height="10" fill="#28AFCA" />
            <rect x="18" y="4" width="10" height="10" fill="#A2B7C8" />
            <rect x="4" y="18" width="10" height="10" fill="#A2B7C8" />
            <rect x="18" y="18" width="10" height="10" fill="#24566C" />
          </svg>
          <div className="flex flex-col leading-none">
            <span className="font-bold text-lg tracking-tight">Aquarius</span>
            <span className="text-xs text-muted-foreground">CDR Dashboard</span>
          </div>
        </Link>
        <nav className="hidden md:flex flex-wrap gap-4 text-sm font-medium justify-end">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className={cn(
                'hover:text-primary transition-colors',
                isActive(l.to, l.match) && 'text-primary',
              )}
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-1 shrink-0" role="group" aria-label={t('common.language')}>
          {(['ru', 'en'] as Lang[]).map((code) => (
            <button
              key={code}
              type="button"
              onClick={() => setLang(code)}
              className={cn(
                'px-2 py-1 rounded text-xs font-semibold uppercase transition-colors',
                lang === code
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground',
              )}
              aria-pressed={lang === code}
            >
              {code}
            </button>
          ))}
        </div>
      </div>
    </header>
  )
}
