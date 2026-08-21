import { Link } from 'react-router-dom'

export function Header() {
  return (
    <header className="border-b border-border bg-card sticky top-0 z-50">
      <div className="container mx-auto flex items-center justify-between h-14 px-4">
        <Link to="/" className="flex items-center gap-3">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Aquarius pixel logo">
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
        <nav className="hidden sm:flex gap-6 text-sm font-medium">
          <Link to="/classic" className="hover:text-primary transition-colors">Classic</Link>
          <Link to="/analytics" className="hover:text-primary transition-colors">Analytics</Link>
          <Link to="/contact-center" className="hover:text-primary transition-colors">Contact Center</Link>
          <Link to="/modern" className="hover:text-primary transition-colors">Modern</Link>
          <Link to="/health" className="hover:text-primary transition-colors">Здоровье</Link>
          <Link to="/dialplan" className="hover:text-primary transition-colors">План нумерации</Link>
          <Link to="/logs" className="hover:text-primary transition-colors">Журналы</Link>
          <Link to="/recordings" className="hover:text-primary transition-colors">Записи</Link>
        </nav>
      </div>
    </header>
  )
}
